import sillyorm
import silly


class XMLId(silly.model.Model):
    _name = "xmlid"

    xmlid = sillyorm.fields.String(length=255)
    model_name = sillyorm.fields.String(length=255)
    model_id = sillyorm.fields.Integer()

    def reverse_lookup(self, model, id):
        record = self.search([("model_name", "=", model), "&", ("model_id", "=", id)])
        if not record:
            return False
        return record.xmlid

    def lookup(self, xmlid, model=None):
        record = self.search([("xmlid", "=", xmlid)])
        if not record:
            return False
        if model is not None and model != record.model_name:
            raise Exception(f"xmlid: expected model {model} but got {record.model_name} (id: {xmlid})")
        return self.env[record.model_name].browse(record.model_id)

    def assign(self, xmlid, record, overwrite=False):
        existing = self.search([("xmlid", "=", xmlid)])
        if existing:
            if not overwrite:
                raise Exception(f"xmlid {xmlid} already exists and can't be overwritten")
            existing.model_id = record.id
            existing.model_name = record._name
        else:
            self.create(
                {
                    "xmlid": xmlid,
                    "model_id": record.id,
                    "model_name": record._name,
                }
            )
