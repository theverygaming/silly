import re
from lxml import etree
import flask
import sillyorm
from . import routes

class View(sillyorm.model.Model):
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
                    read_data = self.env[self.model_name].browse(int(params["id"])).read(read_vals)[0]
                else:
                    # TODO: some sort of default values?
                    read_data = {k: "" for k in read_vals}
                vals["data"] = {fform: self._nojs_convert_type_read(fform, read_data[fname]) for fform, fname in self._nojs_field_name_lookup().items()}
        return vals

    def _nojs_field_lookup(self):
        self.ensure_one()
        field_lookup = {}
        main_tree = etree.fromstring(self.xml).xpath("/main")[0]
        for field_idx, field in enumerate(main_tree.xpath("//field")):
            field_lookup[f"field_{field_idx}"] = dict(field.attrib)
        return field_lookup

    def _nojs_field_name_lookup(self):
        return {k: v["name"] for k, v in self._nojs_field_lookup().items()}

    def _nojs_convert_type_read(self, field, value):
        attrs = self._nojs_field_lookup()[field]
        return value
    
    def _nojs_convert_type_write(self, field, value):
        attrs = self._nojs_field_lookup()[field]
        return value

    def _nojs_expand_xml(self):
        tree = etree.fromstring(self.xml)
        main_tree = tree.xpath("/main")[0]

        for field_idx, field in enumerate(main_tree.xpath("//field")):
            t_call = etree.Element("t", attrib={"t-call": f"webclient_nojs.view_xml_{self.view_type}_widget"})

            attribs = field.attrib

            attribs["form_name"] = f"field_{field_idx}"

            if "widget" not in attribs:
                attribs["widget"] = "str"

            for k, v in attribs.items():
                t_set = etree.Element("t", attrib={"t-set": k})
                t_set.text = v
                t_call.append(t_set)

            parent = field.getparent()
            parent.replace(field, t_call)
        new_xml = "".join(etree.tostring(child, encoding="utf-8").decode("utf-8") for child in main_tree)
        return f"<template>{new_xml}</template>"

    def nojs_render(self, params):
        self.ensure_one()
        view_vals = self._nojs_build_view_vals(params)
        print(f"params: {params} view_vals: {view_vals}")
        expanded_main = self._nojs_expand_xml()
        print(expanded_main)
        return self.env["template"].render(
            f"webclient_nojs.view_xml_{self.view_type}",
            {
                "xml_main": expanded_main,
            } | view_vals,
        )

    def _nojs_handle_post(self, params, post_params):
        match self.view_type:
            case "form":
                match post_params["type"]:
                    case "save":
                        field_id_lookup = self._nojs_field_name_lookup()
                        raw_field_vals = {k: v for k, v in post_params.items() if k in field_id_lookup}
                        # TODO: we need to handle readonly fields here (at the time of writing this XML views don't support them yet though lol)
                        vals = {field_id_lookup[k]: self._nojs_convert_type_write(k, v) for k, v in raw_field_vals.items()}

                        # remove fields we can't write
                        for k in vals.copy():
                            if k in ["id"]:
                                del vals[k]

                        # new record
                        if not "id" in params:
                            params_new = dict(params) # params dict is immutable
                            params_new["id"] = self.env[self.model_name].create(vals).id
                            params_new["view_id"] = self.env["xmlid"].reverse_lookup("webclient_nojs_view", self.id)
                            return {
                                "type": "redirect",
                                "url": flask.url_for(routes.Webclient.webclient2_render_view.endpoint, **params_new),
                            }

                        self.env[self.model_name].browse(int(params["id"])).write(vals)
                        return None

    def nojs_handle_post(self, params, post_params):
        self.ensure_one()
        print(f"post_params: {post_params}")
        action_return = self._nojs_handle_post(params, post_params)
        print(f"action_return: {action_return}")
        if action_return is not None:
            match action_return["type"]:
                case "redirect":
                    return flask.redirect(action_return["url"])
        return self.nojs_render(params)
