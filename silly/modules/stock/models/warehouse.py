import sillyorm
import silly


class StockWarehouse(silly.model.Model):
    _name = "stock.warehouse"

    name = sillyorm.fields.String(length=255, required=True)

    stock_location_id = sillyorm.fields.Many2one("stock.location", required=True)
