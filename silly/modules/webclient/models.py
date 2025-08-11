import sillyorm
import silly


class SillyAbstractBase(silly.model.AbstractModel):
    _name = "core.__silly_abstract_base"
    _extends = "core.__silly_abstract_base"

    def webclient_model_spec(self, traverse_rel=False):
        fetched_rel_specs = {}

        def _model_spec_core(model):
            field_info = {}
            for name, field in model._fields.items():
                field_info[name] = {
                    "type": type(field).__name__,
                    "rel_model": getattr(field, "_foreign_model", None),
                }
                if traverse_rel and (rsp := field_info[name]["rel_model"]):
                    if rsp not in fetched_rel_specs:
                        fetched_rel_specs[rsp] = None  # to prevent infinite recursion
                        fetched_rel_specs[rsp] = _model_spec_core(self.env[rsp])
            return {
                "field_info": field_info,
            }

        ret = _model_spec_core(self)
        if traverse_rel:
            ret["rel_specs"] = fetched_rel_specs
        return ret

    def webclient_read(self, field_names):
        field_name_parts = [x.split(".") for x in field_names]

        def get_field_info(record, name):
            field = record._fields[name]
            data = {
                "objtype": "sillyFieldValue",
            }
            return data

        def get_rel_field_model(record, name):
            field = record._fields[name]
            if not isinstance(field, sillyorm.fields.Many2one):
                return None
            return field._foreign_model

        def read_subfields(record, subfields):
            # get first-level field names
            first_level_fields = list(set(x[0] for x in subfields) | set(["id"]))
            base_data = record.read(first_level_fields)

            for i, rec in enumerate(base_data):
                for field in rec:
                    rel_model = get_rel_field_model(record, field)
                    if rel_model is not None:
                        base_data[i][field] = {
                            "value": {
                                "objtype": "sillyRecordset",
                                "model": rel_model,
                                "records": [
                                    {
                                        "id": {
                                            "objtype": "sillyFieldValue",
                                            "value": rec[field],
                                        },
                                    },
                                ],
                                "spec": self.env[rel_model].webclient_model_spec(),
                            }
                        } | get_field_info(record, field)
                    else:
                        base_data[i][field] = {"value": rec[field]} | get_field_info(record, field)

            # group subfields by their related model
            subfields_by_field = {}
            for sf in filter(lambda x: len(x) > 1, subfields):
                subfields_by_field.setdefault(sf[0], []).append(sf[1:])

            # for each many2one field, gather IDs and do a bulk read
            for field_name, deeper_subfields in subfields_by_field.items():
                submodel_name = get_rel_field_model(record, field_name)
                related_ids = set(
                    rec[field_name]["value"]["records"][0]["id"]["value"]
                    for rec in base_data
                    if rec[field_name]
                )
                related_records = record.env[submodel_name].browse(list(related_ids))
                related_data = read_subfields(related_records, deeper_subfields)

                # map related_data back to base_data
                related_data_by_id = {rec["id"]["value"]: rec for rec in related_data}
                for rec in base_data:
                    rel_id = rec[field_name]["value"]["records"][0]["id"]["value"]
                    if rel_id:
                        rec[field_name]["value"] = {
                            "objtype": "sillyRecordset",
                            "model": submodel_name,
                            "records": [related_data_by_id.get(rel_id)],
                            "spec": self.env[submodel_name].webclient_model_spec(),
                        }
            return base_data

        subfield_data = read_subfields(self, field_name_parts)

        return {
            "objtype": "sillyRecordset",
            "model": self._name,
            "records": subfield_data,
            "spec": self.webclient_model_spec(),
        }

    def webclient_search(self, domain, *args, **kwargs):
        # fix up the domain - JS can only pass lists, not tuples
        for i, op in enumerate(domain):
            if isinstance(op, list):
                domain[i] = tuple(op)
        return super().search(domain, *args, **kwargs)


class View(silly.model.Model):
    _name = "webclient.view"

    model_name = sillyorm.fields.String()
    xml = sillyorm.fields.Text()


class Action(silly.model.Model):
    _name = "webclient.action"

    view_id = sillyorm.fields.Many2one("webclient.view", required=True)
    domain = sillyorm.fields.String(required=True, default="[]")

    def to_dict(self):
        self.ensure_one()
        return {
            "view_id": self.view_id.id,
            "domain": self.domain,
        }


class Menuitem(silly.model.Model):
    _name = "webclient.menuitem"

    name = sillyorm.fields.String(required=True)
    child_ids = sillyorm.fields.One2many("webclient.menuitem", "parent_id")
    parent_id = sillyorm.fields.Many2one("webclient.menuitem")
    action_id = sillyorm.fields.Many2one("webclient.action")

    def get_dict(self):
        self.ensure_one()
        d = {
            "id": self.id,
            "name": self.name,
        }
        if self.action_id:
            d["action"] = self.action_id.to_dict()
        return d

    def get_submenus_dict(self):
        self.ensure_one()
        ret = []
        for child in self.child_ids:
            x = child.get_dict()
            if child.child_ids:
                x["children"] = child.get_submenus_dict()
            ret.append(x)
        return ret

    def get_main_menu_dict(self):
        main_items = self.search([("parent_id", "=", None)])
        return [rec.get_dict() for rec in main_items]
