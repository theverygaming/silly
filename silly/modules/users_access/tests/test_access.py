import sillyorm
from silly.tests import TransactionCase
from silly.modules.users_access.models import SillyAccessError


class UsersAccessTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user_1 = self.env["users.user"].create({})
        self.group_1 = self.env["users_access.group"].create(
            {
                "name": "group WITH user_1 member",
                # FIXME: sillyORM should support this shi
                # "user_ids": sillyorm.fields.Many2xCommand.link(self.user_1),
            }
        )
        self.group_1.user_ids = sillyorm.fields.Many2xCommand.link(self.user_1)
        self.group_2 = self.env["users_access.group"].create(
            {
                "name": "group WITHOUT user_1 member",
            }
        )

    def _check_access(self, model, env, ptypes, valid_vals):
        def c_perm_create():
            env[model].create(valid_vals)

        create_fns = [c_perm_create]

        def c_perm_read1():
            created_id = env.sudo()[model].create(valid_vals).id
            env[model].search([])

        def c_perm_read2():
            created_id = env.sudo()[model].create(valid_vals).id
            env[model].browse(created_id).read(["id"] + [str(k) for k in valid_vals.keys()])

        def c_perm_read3():
            created_id = env.sudo()[model].create(valid_vals).id
            excs = []
            for k in valid_vals:
                try:
                    getattr(env[model].browse(created_id), k)
                except SillyAccessError as e:
                    excs.append(e)
            if excs:
                if len(excs) != len(valid_vals.keys()):
                    raise Exception("not all attrs raised errors")
                type0 = type(excs[0])
                for exc in excs:
                    if type(exc) != type0:
                        raise Exception("not the same exception raised for all write attrs")
                raise excs[0]  # we won't raise all of them - just one

        read_fns = [c_perm_read1, c_perm_read2, c_perm_read3]

        def c_perm_write1():
            created_id = env.sudo()[model].create(valid_vals).id
            env[model].browse(created_id).write(valid_vals)

        def c_perm_write2():
            created_id = env.sudo()[model].create(valid_vals).id
            excs = []
            for k, v in valid_vals.items():
                try:
                    setattr(env[model].browse(created_id), k, v)
                except SillyAccessError as e:
                    excs.append(e)
            if excs:
                if len(excs) != len(valid_vals.keys()):
                    raise Exception("not all attrs raised errors")
                type0 = type(excs[0])
                for exc in excs:
                    if type(exc) != type0:
                        raise Exception("not the same exception raised for all write attrs")
                raise excs[0]  # we won't raise all of them - just one

        write_fns = [c_perm_write1, c_perm_write2]

        def c_perm_delete():
            created_id = env.sudo()[model].create(valid_vals).id
            env[model].browse(created_id).delete()

        delete_fns = [c_perm_delete]

        with_e = []
        without_e = []

        if "perm_create" in ptypes:
            without_e += create_fns
        else:
            with_e += create_fns
        if "perm_read" in ptypes:
            without_e += read_fns
        else:
            with_e += read_fns
        if "perm_write" in ptypes:
            without_e += write_fns
        else:
            with_e += write_fns
        if "perm_delete" in ptypes:
            without_e += delete_fns
        else:
            with_e += delete_fns

        for fn in with_e:
            print(f"with_e running {fn}")
            with self.assertRaises(SillyAccessError) as e:
                fn()
        for fn in without_e:
            print(f"without_e running {fn}")
            fn()

    def test_model_access(self):
        # no group
        ma = self.env["users_access.model_access"].create(
            {
                "name": "core.module access",
                "model": "core.module",
                "perm_create": False,
                "perm_read": False,
                "perm_write": False,
                "perm_delete": False,
                # no group set -> generic access for every user
            }
        )
        new_env = self.env.with_uid(self.user_1.id)

        # no access at all.. all perms false
        self._check_access("core.module", new_env, [], {"name": "a"})

        # read access
        ma.perm_read = True
        self._check_access("core.module", new_env, ["perm_read"], {"name": "a"})
        # group set (user_1 is member): user can still access
        ma.group_id = self.group_1
        self._check_access("core.module", new_env, ["perm_read"], {"name": "a"})
        # group set (user_1 is no member)
        ma.group_id = self.group_2
        self._check_access("core.module", new_env, [], {"name": "a"})
