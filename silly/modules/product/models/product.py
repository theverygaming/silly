import sillyorm
import silly


class ProductProduct(silly.model.Model):
    _name = "product.product"

    name = sillyorm.fields.String(length=255, required=True)
    description = sillyorm.fields.Text()

    category_id = sillyorm.fields.Many2one("product.category")
