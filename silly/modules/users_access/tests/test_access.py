import sillyorm
from silly.tests import TransactionCase
from silly.modules.users_access.models import SillyAccessError


class UsersAccessTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user_1 = self.env["users.user"].create({})
        self.group_1 = self.env["users_access.group"].create(
            {
                "name": "",
                "user_ids": sillyorm.fields.Many2xCommand.link(self.user_1),
            }
        )

    def test_model_access(self):
        # no group
        ma = self.env["users_access.model_access"].create(
            {
                "name": "core.module access",
                "model": "core.module",
                "perm_create": False,
                "perm_write": False,
                "perm_read": False,
                "perm_delete": False,
                # no group set -> generic access for every user
            }
        )
        new_env = self.env.with_uid(self.user_1.id)
        with self.assertRaises(SillyAccessError) as e:
            new_env["core.module"].search([])
