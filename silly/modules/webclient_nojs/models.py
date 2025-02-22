import sillyorm

class View(sillyorm.model.Model):
    _name = "webclient_nojs_view"

    model_name = sillyorm.fields.String(length=255)
    view_type = sillyorm.fields.Selection(["list", "form"], length=255)
    xml = sillyorm.fields.Text()
