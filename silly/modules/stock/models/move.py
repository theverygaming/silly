import datetime
import sillyorm
import silly


class StockMove(silly.model.Model):
    _name = "stock.move"

    product_id = sillyorm.fields.Many2one("product.product")
    lot_id = sillyorm.fields.Many2one("stock.lot")

    quantity = sillyorm.fields.Float(required=True)

    source_location_id = sillyorm.fields.Many2one("stock.location", required=True)
    destination_location_id = sillyorm.fields.Many2one("stock.location", required=True)

    timestamp = sillyorm.fields.Datetime(tzinfo=datetime.UTC, convert_tz=True, required=True)

    @sillyorm.model.constraints("product_id", "lot_id")
    def _constraint_product_id_lot_id(self):
        for record in self:
            if bool(record.product_id) == bool(record.lot_id):
                raise silly.exceptions.SillyValidationError(
                    "only one of product_id or lot_id may be set"
                )

    @sillyorm.model.constraints("source_location_id", "destination_location_id")
    def _constraint_locations(self):
        for record in self:
            if record.source_location_id.id == record.destination_location_id.id:
                raise silly.exceptions.SillyValidationError(
                    "source and destination locations may not be equal"
                )
