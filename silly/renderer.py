import ast
import copy
from lxml import etree
import sillyorm


def _safe_eval(node, vars, value=None):
    # print(f"entering _safe_eval vars: {vars} value: {value}")
    # print(ast.dump(node, indent=2))
    if isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Name):
            assert isinstance(node.value.ctx, ast.Load)
            return vars[node.value.id]
        if isinstance(node.value, ast.Subscript):
            return _safe_eval(node.value, vars, vars)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        assert isinstance(node.ctx, ast.Load)
        return node.id
    if isinstance(node, ast.Subscript):
        assert isinstance(node.ctx, ast.Load)
        if isinstance(node.value, ast.Name):
            # load variable
            var = value[_safe_eval(node.value, vars)]
        else:
            # we need to go deeper
            var = _safe_eval(node.value, vars, value)
        # do the actual subscript
        return var[_safe_eval(node.slice, vars)]
    return None


def safe_eval(expr, vars):
    # return vars[expr]
    nodes = ast.parse(expr).body
    if len(nodes) != 1:
        raise Exception("safe_eval expected one AST node")
    ret = _safe_eval(nodes[0], vars)
    # print(f"exiting safe_eval with {ret}")
    return ret


_HTML_SELFCLOSING_TAGS = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
    "command",
    "keygen",
    "menuitem",
    "frame",
]


def _render_html(get_template_fn, element, render_ctx, render_self=False):
    element = copy.deepcopy(element)  # NOTE: miiiight have broken _something_?

    def f_render_element_beg(render_tag, render_text):
        output = ""
        if render_tag:
            output += f"<{element.tag}" + (" " if len(element.items()) else "")
            for k, v in element.items():
                output += f'{k}="{v}"'
            output += f">"
        if render_text and element.text is not None:
            output += element.text
        return output

    def f_render_children():
        output = ""
        for child in element:
            output += _render_html(get_template_fn, child, render_ctx, render_self=True)
        return output

    def f_render_element_end(render_tag, render_tail):
        output = ""
        if render_tag and element.tag not in _HTML_SELFCLOSING_TAGS:
            output += f"</{element.tag}>"
        if render_tail and element.tail is not None:
            output += element.tail
        return output

    def process_attrs(render_tag, render_tail, render_text, render_children):
        output = ""
        for k, v in element.attrib.items():
            # FIXME: a bunch of these ofc allow injecting HTML (t-att for example), they do gotta be fixed
            # t-att-
            if k.startswith("t-att-"):
                del element.attrib[k]
                val = safe_eval(v, render_ctx)
                # if an attribute evaluates to None, don't add it at all
                if val is not None:
                    element.attrib[k.removeprefix("t-att-")] = val
                continue
            # t-raw
            if k == "t-raw":
                del element.attrib[k]
                element.text = safe_eval(v, render_ctx)
                continue
            # t-set
            if k == "t-set":
                render_tag = render_text = render_children = False
                render_ctx[v] = element.text if element.text is not None else ""
                render_ctx[v] += f_render_children()
                continue
            # t-call
            if k == "t-call":
                render_tag = render_tail = render_text = render_children = False
                render_ctx["0"] = (
                    element.text if element.text is not None else ""
                ) + f_render_children()
                output += _render_html(get_template_fn, get_template_fn(v), render_ctx)
                continue
            # t-foreach
            if k == "t-foreach":
                render_tag = render_tail = render_text = render_children = False
                for x in safe_eval(v, render_ctx):
                    render_ctx[element.attrib["t-as"]] = x
                    output += f_render_children()
                continue
            # t-strip
            if k.startswith("t-strip-"):
                del element.attrib[k]
                st = k.removeprefix("t-strip-")
                match st:
                    case "text":
                        element.text = element.text.lstrip(v)
                    case "tail":
                        element.tail = element.tail.rstrip(v)
                    case _:
                        raise Exception(f'invalid {k}="{v}"')
                continue
        return output, render_tag, render_tail, render_text, render_children

    if not isinstance(element.tag, str):
        raise Exception(f"unknown tag {element.tag}")
    render_tag = render_tail = render_self
    render_text = render_children = True
    # we don't render the t tag
    if element.tag == "t":
        render_tag = False
    output, render_tag, render_tail, render_text, render_children = process_attrs(
        render_tag, render_tail, render_text, render_children
    )
    output += f_render_element_beg(render_tag, render_text)
    if render_children:
        output += f_render_children()
    output += f_render_element_end(render_tag, render_tail)
    return output


class Template(sillyorm.model.Model):
    _name = "template"

    xml = sillyorm.fields.Text()

    def render(self, xmlid, vals):
        def get_template(xmlid):
            template = self.env.xmlid_lookup("template", xmlid)
            if not template:
                raise Exception(f"template with xmlid '{xmlid}' not found in database")
            return etree.fromstring(template.xml)

        return _render_html(get_template, get_template(xmlid), vals)
