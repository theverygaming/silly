import sillyorm
import silly


class ProductCategory(silly.model.Model):
    _name = "product.category"

    name = sillyorm.fields.String(length=255, required=True)
    parent_id = sillyorm.fields.Many2one("product.category")
