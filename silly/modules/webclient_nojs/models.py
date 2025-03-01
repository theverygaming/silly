import re
from lxml import etree
import flask
import sillyorm
from . import routes
import silly


class View(silly.model.Model):
    _name = "webclient_nojs_view"

    model_name = sillyorm.fields.String(length=255)
    view_type = sillyorm.fields.Selection(["list", "form"], length=255)
    xml = sillyorm.fields.Text()

    def _nojs_build_view_vals(self, params):
        vals = {}
        match self.view_type:
            case "form":
                read_vals = list(set(self._nojs_field_name_lookup().values()))
                if "id" in params:
                    read_data = (
                        self.env[self.model_name].browse(int(params["id"])).read(read_vals)[0]
                    )
                else:
                    # TODO: some sort of default values?
                    read_data = {k: "" for k in read_vals}
                vals["data"] = {
                    fform: self._nojs_convert_type_read(fform, read_data[fname])
                    for fform, fname in self._nojs_field_name_lookup().items()
                }
        return vals

    def _nojs_field_lookup(self):
        self.ensure_one()
        field_lookup = {}
        main_tree = etree.fromstring(self.xml).xpath("/view/main")[0]
        for field_idx, field in enumerate(main_tree.xpath("//field")):
            field_lookup[f"field_{field_idx}"] = dict(field.attrib)
        return field_lookup

    def _nojs_field_name_lookup(self):
        return {k: v["name"] for k, v in self._nojs_field_lookup().items()}

    def _nojs_convert_type_read(self, field, value):
        attrs = self._nojs_field_lookup()[field]
        if value is None:
            return ""
        match attrs["widget"]:
            case "string" | "integer" | "float":
                return str(value)
        raise Exception(f"unknown widget '{attrs['widget']}'")

    def _nojs_convert_type_write(self, field, value):
        attrs = self._nojs_field_lookup()[field]
        if value is None:
            return ""
        match attrs["widget"]:
            case "string":
                return str(value)
            case "integer":
                return int(value)
            case "float":
                return float(value)
        raise Exception(f"unknown widget '{attrs['widget']}'")

    def _nojs_expand_xml(self):
        tree = etree.fromstring(self.xml)

        header_tree = tree.xpath("/view/header")[0]
        for field_idx, field in enumerate(header_tree.xpath("//button")):
            t_call = etree.Element(
                "t", attrib={"t-call": f"webclient_nojs.view_xml_{self.view_type}_button"}
            )

            attribs = field.attrib

            for attrib in ["label", "type", "target"]:
                if attrib not in attribs:
                    raise Exception(f"attribute '{attrib}' missing")

            if not attribs["type"] == "action":
                raise Exception(f"button type '{attribs['type']}' not supported")

            for k, v in attribs.items():
                t_set = etree.Element("t", attrib={"t-set": k})
                t_set.text = v
                t_call.append(t_set)

            # attribs itself is specified in another t-set in case a button wants to
            # define default values (othewise might get undefined variable errors)!
            t_call.append(
                etree.Element(
                    "t", attrib={"t-set": "button_attribs", "t-value": repr(dict(attribs))}
                )
            )

            parent = field.getparent()
            parent.replace(field, t_call)
        new_header_xml = "".join(
            etree.tostring(child, encoding="utf-8").decode("utf-8") for child in header_tree
        )

        main_tree = tree.xpath("/view/main")[0]
        for field_idx, field in enumerate(main_tree.xpath("//field")):
            t_call = etree.Element(
                "t", attrib={"t-call": f"webclient_nojs.view_xml_{self.view_type}_widget"}
            )

            attribs = field.attrib

            attribs["form_name"] = f"field_{field_idx}"

            for attrib in ["widget"]:
                if attrib not in attribs:
                    raise Exception(f"attribute '{attrib}' missing")

            for k, v in attribs.items():
                t_set = etree.Element("t", attrib={"t-set": k})
                t_set.text = v
                t_call.append(t_set)

            # attribs itself is specified in another t-set in case a widget wants to
            # define default values (othewise might get undefined variable errors)!
            t_call.append(
                etree.Element(
                    "t", attrib={"t-set": "widget_attribs", "t-value": repr(dict(attribs))}
                )
            )

            parent = field.getparent()
            parent.replace(field, t_call)
        new_main_xml = "".join(
            etree.tostring(child, encoding="utf-8").decode("utf-8") for child in main_tree
        )

        return {
            "header": f"<template>{new_header_xml}</template>",
            "main": f"<template>{new_main_xml}</template>",
        }

    def nojs_render(self, params, **kwargs):
        self.ensure_one()
        view_vals = self._nojs_build_view_vals(params)
        print(f"params: {params} view_vals: {view_vals}")
        expanded_xml = self._nojs_expand_xml()
        print(expanded_xml)
        return self.env["template"].render(
            f"webclient_nojs.view_xml_{self.view_type}",
            {
                "xml_header": expanded_xml["header"],
                "xml_main": expanded_xml["main"],
                "action_msg": kwargs.get("action_msg"),
            }
            | view_vals,
        )

    def _nojs_handle_post(self, params, post_params):
        match self.view_type:
            case "form":
                match post_params["type"]:
                    case "save":
                        field_id_lookup = self._nojs_field_name_lookup()
                        raw_field_vals = {
                            k: v for k, v in post_params.items() if k in field_id_lookup
                        }
                        # TODO: we need to handle readonly fields here (at the time of writing this XML views don't support them yet though lol)
                        vals = {
                            field_id_lookup[k]: self._nojs_convert_type_write(k, v)
                            for k, v in raw_field_vals.items()
                        }

                        # remove fields we can't write
                        for k in vals.copy():
                            if k in ["id"]:
                                del vals[k]

                        # new record
                        if not "id" in params:
                            params_new = dict(params)  # params dict is immutable
                            params_new["id"] = self.env[self.model_name].create(vals).id
                            params_new["view_id"] = self.env["xmlid"].reverse_lookup(
                                "webclient_nojs_view", self.id
                            )
                            return {
                                "type": "redirect",
                                "url": flask.url_for(
                                    routes.Webclient.webclient2_render_view.endpoint, **params_new
                                ),
                            }

                        self.env[self.model_name].browse(int(params["id"])).write(vals)
                        return None
                    case "action":
                        if "id" in params:
                            record = self.env[self.model_name].browse(int(params["id"]))
                        else:
                            record = self.env[self.model_name]
                        fn = getattr(record, f"action_{post_params['action']}")
                        return fn()

    def nojs_handle_post(self, params, post_params):
        self.ensure_one()
        print(f"post_params: {post_params}")
        action_return = self._nojs_handle_post(params, post_params)
        print(f"action_return: {action_return}")
        if action_return is not None:
            match action_return["type"]:
                case "redirect":
                    return flask.redirect(action_return["url"])
                case "message":
                    return self.nojs_render(params, action_msg=action_return["message"])
        return self.nojs_render(params)
