import datetime
import sillyorm
import silly


class StockLot(silly.model.Model):
    _name = "stock.lot"

    name = sillyorm.fields.String(length=255, required=True)

    product_id = sillyorm.fields.Many2one("product.product", required=True)
