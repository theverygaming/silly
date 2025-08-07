from silly.tests import TransactionCase


class XMLIDTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.sample_record_1 = self.env["core.template"].create(
            {
                "xml": "test 1",
            }
        )
        self.sample_record_2 = self.env["core.template"].create(
            {
                "xml": "test 2",
            }
        )
        self.sample_record_3 = self.env["core.template"].create(
            {
                "xml": "test 3",
            }
        )

    def test_lookups(self):
        # create a couple xmlids
        self.env["core.xmlid"].assign(
            "core.test_lookup_xmlid1", self.sample_record_1, source_module="core"
        )
        self.env["core.xmlid"].assign(
            "core.test_lookup_xmlid2", self.sample_record_2, source_module="core"
        )
        # lookup
        self.assertEqual(
            repr(self.env["core.xmlid"].lookup("core.test_lookup_xmlid1")),
            f"core.template[{self.sample_record_1.id}]",
        )
        self.assertEqual(
            repr(self.env["core.xmlid"].lookup("core.test_lookup_xmlid2")),
            f"core.template[{self.sample_record_2.id}]",
        )
        self.assertFalse(
            self.env["core.xmlid"].lookup("core.thisxmlidisinvalid"),
        )
        # lookup with incorrect model
        with self.assertRaises(Exception) as e:
            self.env["core.xmlid"].lookup("core.test_lookup_xmlid2", model="core.xmlid")
        self.assertEqual(
            str(e.exception),
            "xmlid: expected model core.xmlid but got core.template (id: core.test_lookup_xmlid2)",
        )
        # reverse lookup
        self.assertEqual(
            self.env["core.xmlid"].reverse_lookup("core.template", self.sample_record_1.id),
            "core.test_lookup_xmlid1",
        )
        self.assertEqual(
            self.env["core.xmlid"].reverse_lookup("core.template", self.sample_record_2.id),
            "core.test_lookup_xmlid2",
        )
        self.assertFalse(
            self.env["core.xmlid"].reverse_lookup("thismodeldoesnotexist", 1),
        )

    def test_assign(self):
        # create a couple xmlids
        self.env["core.xmlid"].assign(
            "core.test_assign_xmlid1", self.sample_record_1, source_module="core"
        )
        self.env["core.xmlid"].assign(
            "core.test_assign_xmlid2", self.sample_record_2, source_module="core"
        )
        # try overwriting without allowing overwrite
        with self.assertRaises(Exception) as e:
            self.env["core.xmlid"].assign(
                "core.test_assign_xmlid2", self.sample_record_3, source_module="core"
            )
        self.assertEqual(
            str(e.exception),
            "xmlid core.test_assign_xmlid2 already exists and can't be overwritten",
        )
        # overwrite one of the xmlids
        self.env["core.xmlid"].assign(
            "core.test_assign_xmlid2",
            self.sample_record_3,
            source_module="core",
            overwrite=True,
        )
        # look them up
        self.assertEqual(
            repr(self.env["core.xmlid"].lookup("core.test_assign_xmlid1")),
            f"core.template[{self.sample_record_1.id}]",
        )
        self.assertEqual(
            repr(self.env["core.xmlid"].lookup("core.test_assign_xmlid2")),
            f"core.template[{self.sample_record_3.id}]",
        )
