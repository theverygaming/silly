import sillyorm


class XMLId(sillyorm.model.Model):
    _name = "xmlid"

    xmlid = sillyorm.fields.String(length=255)
    model_id = sillyorm.fields.Integer()
    model_name = sillyorm.fields.String(length=255)

    def lookup(self, model, xmlid):
        domain = [("xmlid", "=", xmlid)]
        if model:
            domain += ["&", ("model_name", "=", model)]
        record = self.search([("xmlid", "=", xmlid)])
        if not record:
            return False
        return self.env[record.model_name].browse(record.model_id)

    def assign(self, xmlid, record, overwrite=False):
        existing = self.search([("xmlid", "=", xmlid)])
        if existing:
            if not overwrite:
                raise Exception(f"xmlid {xmlid} already exists and can't be overwritten")
            existing.model_id = record.id
            existing.model_name = record._name
        else:
            self.create({
                "xmlid": xmlid,
                "model_id": record.id,
                "model_name": record._name,
            })
