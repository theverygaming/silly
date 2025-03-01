import logging
import ast
import copy
from lxml import etree
import sillyorm
from . import model

_logger = logging.getLogger(__name__)


# FIXME: we do kinda want a safer eval
def horribly_unsafe_eval(expr, vars):
    try:
        ret = eval(expr, {}, vars)
    except Exception as e:
        _logger.error("Error evalutating %s - available vars: %s", repr(expr), repr(vars))
        raise e
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
    try:
        return _def_render_html(get_template_fn, element, render_ctx, render_self=render_self)
    except Exception as e:
        # TODO: maybe later the exception should be done differently
        if not hasattr(e, "_render_html_error_bubbling"):
            _logger.error(
                "Rendering error, %s Somewhere inside:\n%s",
                repr(e),
                etree.tostring(element, pretty_print=True, encoding="utf-8").decode("utf-8"),
            )
            setattr(e, "_render_html_error_bubbling", True)
        raise e


def _def_render_html(get_template_fn, element, render_ctx, render_self=False):
    element = copy.deepcopy(element)  # NOTE: miiiight have broken _something_?

    def f_render_element_beg(render_tag, render_text):
        output = ""
        if render_tag:
            output += f"<{element.tag}" + (" " if len(element.items()) else "")
            for i, (k, v) in enumerate(element.items()):
                output += f'{k}="{v}"{' ' if i != len(element.items()) - 1 else ''}'
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
                val = horribly_unsafe_eval(v, render_ctx)
                # if an attribute evaluates to None, don't add it at all
                if val is not None:
                    element.attrib[k.removeprefix("t-att-")] = str(val)
                continue
            # t-raw
            if k == "t-raw":
                del element.attrib[k]
                val = horribly_unsafe_eval(v, render_ctx)
                element.text = str(val) if val is not None else None
                continue
            # t-render
            if k == "t-render":
                del element.attrib[k]
                val = horribly_unsafe_eval(v, render_ctx)
                render_tag = render_text = render_children = False
                render_ctx["0"] = (
                    element.text if element.text is not None else ""
                ) + f_render_children()
                output += _render_html(get_template_fn, etree.fromstring(val), render_ctx)
                continue
            # t-set / t-value
            if k == "t-set":
                render_tag = render_text = render_children = False
                if "t-value" not in element.attrib:
                    # Temporary variable so we can overwrite
                    # variables with the same name of the variable we are setting
                    # in t-set
                    set_val = element.text if element.text is not None else ""
                    set_val += f_render_children()
                    render_ctx[v] = set_val
                else:
                    render_ctx[v] = horribly_unsafe_eval(element.attrib["t-value"], render_ctx)
                continue
            # t-call
            if k == "t-call":
                render_tag = render_text = render_children = False
                render_ctx["0"] = (
                    element.text if element.text is not None else ""
                ) + f_render_children()
                output += _render_html(get_template_fn, get_template_fn(v), render_ctx)
                continue
            # t-foreach / t-as
            if k == "t-foreach":
                render_tag = render_text = render_children = False
                for x in horribly_unsafe_eval(v, render_ctx):
                    render_ctx[element.attrib["t-as"]] = x
                    output += element.text if element.text is not None else ""
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
            # t-if
            if k == "t-if":
                ev_res = horribly_unsafe_eval(v, render_ctx)
                if ev_res:
                    del element.attrib[k]
                    continue
                else:
                    render_tag = render_text = render_children = False
                    break
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


class Template(model.Model):
    _name = "template"

    xml = sillyorm.fields.Text()

    def render(self, xmlid, vals):
        def get_template(xmlid):
            template = self.env.xmlid_lookup("template", xmlid)
            if not template:
                raise Exception(f"template with xmlid '{xmlid}' not found in database")
            return etree.fromstring(template.xml)

        return _render_html(get_template, get_template(xmlid), vals)
