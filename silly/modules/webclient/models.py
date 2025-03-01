import sillyorm
import silly


class ViewType(silly.model.Model):
    _name = "view_type"

    component_name = sillyorm.fields.String(length=255)


class View(silly.model.Model):
    _name = "view"

    model_name = sillyorm.fields.String(length=255)
    type_id = sillyorm.fields.Many2one("view_type")
    xml = sillyorm.fields.Text()
