import sillyorm
import silly


class SillyAbstractBase(silly.model.AbstractModel):
    _name = "__silly_abstract_base"
    _extends = "__silly_abstract_base"

    def web_read(self, field_names):
        field_name_parts = [x.split(".") for x in field_names]

        def get_field_info(record, name):
            field = record._fields[name]
            data = {
                "objtype": "sillyFieldValue",
                "type": type(field).__name__,
                "rel_model": getattr(field, "_foreign_model", None),
            }
            return data

        def get_rel_field_model(record, name):
            field = record._fields[name]
            if not isinstance(field, sillyorm.fields.Many2one):
                raise Exception("only many2one supported")
            return field._foreign_model

        def read_subfields(record, subfields):
            # get first-level field names
            first_level_fields = list(set(x[0] for x in subfields) | set(["id"]))
            base_data = record.read(first_level_fields)

            for i, rec in enumerate(base_data):
                for field in rec:
                    base_data[i][field] = {"value": rec[field]} | get_field_info(record, field)

            # group subfields by their related model
            subfields_by_field = {}
            for sf in filter(lambda x: len(x) > 1, subfields):
                subfields_by_field.setdefault(sf[0], []).append(sf[1:])

            # for each many2one field, gather IDs and do a bulk read
            for field_name, deeper_subfields in subfields_by_field.items():
                submodel_name = get_rel_field_model(record, field_name)
                related_ids = set(rec[field_name]["value"] for rec in base_data if rec[field_name])
                related_records = record.env[submodel_name].browse(list(related_ids))
                related_data = read_subfields(related_records, deeper_subfields)

                # map related_data back to base_data
                related_data_by_id = {rec["id"]["value"]: rec for rec in related_data}
                for rec in base_data:
                    rel_id = rec[field_name]["value"]
                    if rel_id:
                        rec[field_name]["value"] = {
                            "objtype": "sillyRecordset",
                            "model": submodel_name,
                            "records": [related_data_by_id.get(rel_id)],
                        }
            return base_data

        subfield_data = read_subfields(self, field_name_parts)

        return {
            "objtype": "sillyRecordset",
            "model": self._name,
            "records": subfield_data,
        }


class ViewType(silly.model.Model):
    _name = "view_type"

    component_name = sillyorm.fields.String(length=255)


class View(silly.model.Model):
    _name = "view"

    model_name = sillyorm.fields.String(length=255)
    type_id = sillyorm.fields.Many2one("view_type")
    xml = sillyorm.fields.Text()
