import datetime
import sillyorm
import silly


class StockLocation(silly.model.Model):
    _name = "stock.location"

    name = sillyorm.fields.String(length=255, required=True)

    parent_id = sillyorm.fields.Many2one("stock.location")
    child_ids = sillyorm.fields.One2many("stock.location", "parent_id")

    def get_all_children(self):
        def _collect_children(recs):
            all_children = []
            for rec in recs:
                if rec.child_ids:
                    all_children += rec.child_ids.ids
                    all_children += _collect_children(rec.child_ids)
            return all_children

        return self.browse(_collect_children(self))

    def compute_quantities(self, tmax=None):
        location_product_qty_map = {}

        for child_loc in self.get_all_children():
            res = child_loc.compute_quantities_single(tmax=tmax)
            if res:
                location_product_qty_map[child_loc.id] = res

        return location_product_qty_map

    def compute_quantities_single(self, tmax=None):
        self.ensure_one()
        if tmax is None:
            tmax = datetime.datetime.now(datetime.UTC)
        moves = self.env["stock.move"].search(
            [
                ("timestamp", "<=", tmax),
                "&",
                "(",
                ("source_location_id", "=", self.id),
                "|",
                ("destination_location_id", "=", self.id),
                ")",
            ],
            order_by="timestamp",
        )

        product_qty_map = {}

        for move in moves:
            if move.product_id:
                key = (move.product_id.id, None)
            else:
                key = (move.lot_id.product_id.id, move.lot_id.id)
            if key not in product_qty_map:
                product_qty_map[key] = 0.0

            # moved into or out of?
            if move.destination_location_id.id == self.id:
                product_qty_map[key] += move.quantity
            else:
                product_qty_map[key] -= move.quantity

        return product_qty_map
