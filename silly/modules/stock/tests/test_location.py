import random
import datetime
import sillyorm
import silly
from silly.tests import TransactionCase


class UsersAccessTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.random = random.Random(1)
        self.loc_main = self.env["stock.location"].create(
            {
                "name": "main",
            }
        )
        self.warehouse = self.env["stock.warehouse"].create(
            {
                "name": "WH1",
                "stock_location_id": self.loc_main.id,
            }
        )
        self.locs = []
        for i in range(1, 5):
            self.locs.append(
                self.env["stock.location"].create(
                    {
                        "name": f"Shelf {i}",
                        "parent_id": self.loc_main.id,
                    }
                )
            )
            self.locs.append(
                self.env["stock.location"].create(
                    {
                        "name": f"Shelf {i} child",
                        "parent_id": self.locs[-1].id,
                    }
                )
            )

        self.products = []
        for pn in range(1, 5):
            self.products.append(
                self.env["product.product"].create(
                    {
                        "name": f"Product {pn}",
                    }
                )
            )

        self.lots = []
        for product in self.products:
            for i in range(1, 3):
                self.lots.append(
                    self.env["stock.lot"].create(
                        {
                            "name": f"Lot {i} of Product {product}",
                            "product_id": product.id,
                        }
                    )
                )

        self.qty_location_map = {}
        for loc in self.locs:
            self.qty_location_map[loc.id] = {}
            for product in self.products:
                qty = self.random.randint(0, 5)
                if qty == 0:
                    continue
                self.qty_location_map[loc.id][(product.id, None)] = float(qty)
                n_quants = 4
                # +1 because we want to test moving away something and putting it back
                for i in range(n_quants + 2):
                    source_location_id = (
                        self.env["core.xmlid"].lookup("stock.location_inventory_adjustment").id
                    )
                    destination_location_id = loc.id
                    # move something away
                    if i == 2:
                        destination_location_id = source_location_id
                        source_location_id = loc.id
                    self.env["stock.move"].create(
                        {
                            "product_id": product.id,
                            "quantity": float(qty) / n_quants,
                            "source_location_id": source_location_id,
                            "destination_location_id": destination_location_id,
                            "timestamp": datetime.datetime.now(datetime.UTC),
                        }
                    )
            for lot in self.lots:
                qty = self.random.randint(0, 5)
                if qty == 0:
                    continue
                self.qty_location_map[loc.id][(lot.product_id.id, lot.id)] = float(qty)
                n_quants = 4
                # +1 because we want to test moving away something and putting it back
                for i in range(n_quants + 2):
                    source_location_id = (
                        self.env["core.xmlid"].lookup("stock.location_inventory_adjustment").id
                    )
                    destination_location_id = loc.id
                    # move something away
                    if i == 2:
                        destination_location_id = source_location_id
                        source_location_id = loc.id
                    self.env["stock.move"].create(
                        {
                            "lot_id": lot.id,
                            "quantity": float(qty) / n_quants,
                            "source_location_id": source_location_id,
                            "destination_location_id": destination_location_id,
                            "timestamp": datetime.datetime.now(datetime.UTC),
                        }
                    )

    def test_stock_compute_quantities(self):
        def _compare_dict(d1, d2):
            if not isinstance(d1, dict) and not isinstance(d2, dict):
                return False
            if d1.keys() != d2.keys():
                return False
            for k, v in d1.items():
                if isinstance(v, dict):
                    if not _compare_dict(v, d2[k]):
                        return False
                if v != d2[k]:
                    return False
            return True

        # correct qtys
        self.assertTrue(
            _compare_dict(
                self.loc_main.compute_quantities(),
                self.qty_location_map,
            )
        )

        # correct output with tmax set
        self.assertEqual(
            self.locs[0].compute_quantities(
                tmax=datetime.datetime(1980, 1, 1, tzinfo=datetime.UTC)
            ),
            {},
        )

    def test_stock_compute_quantities_single(self):
        # correct qtys
        for loc in self.locs:
            self.assertEqual(
                loc.compute_quantities_single(),
                self.qty_location_map[loc.id],
            )

        # correct output with tmax set
        self.assertEqual(
            self.locs[0].compute_quantities_single(
                tmax=datetime.datetime(1980, 1, 1, tzinfo=datetime.UTC)
            ),
            {},
        )

    def test_stock_move_constraints(self):
        with self.assertRaises(silly.exceptions.SillyValidationError) as e:
            self.env["stock.move"].create(
                {
                    "product_id": self.products[0].id,
                    "quantity": 1.0,
                    "source_location_id": self.loc_main.id,
                    "destination_location_id": self.loc_main.id,
                    "timestamp": datetime.datetime.now(datetime.UTC),
                }
            )
        self.assertEqual(
            str(e.exception),
            "source and destination locations may not be equal",
        )

        with self.assertRaises(silly.exceptions.SillyValidationError) as e:
            self.env["stock.move"].create(
                {
                    "product_id": self.products[0].id,
                    "lot_id": self.lots[0].id,
                    "quantity": 1.0,
                    "source_location_id": self.loc_main.id,
                    "destination_location_id": self.locs[0].id,
                    "timestamp": datetime.datetime.now(datetime.UTC),
                }
            )
        self.assertEqual(
            str(e.exception),
            "only one of product_id or lot_id may be set",
        )
