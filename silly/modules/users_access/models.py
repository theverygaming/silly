import sillyorm
import silly


class SillyAccessError(silly.exceptions.SillyException):
    pass


class CustomEnvironment(silly.sillyorm_ext.Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.as_superuser = True
        self.uid = None

    def sudo(self):
        if self.as_superuser and self.uid is None:
            return self
        clone = self.clone()
        clone.as_superuser = True
        clone.uid = None
        return clone

    def with_uid(self, uid):
        clone = self.clone()
        clone.uid = uid
        clone.as_superuser = False
        return clone


class SillyAbstractBase(silly.model.AbstractModel):
    _name = "core.__silly_abstract_base"
    _extends = "core.__silly_abstract_base"

    def _check_access_rights(self, perm):
        if not isinstance(self.env, CustomEnvironment):
            return
        if self.env.as_superuser:
            return
        if self.env.uid is None:
            raise SillyAccessError("no UID set and we are not running as superuser")
        env_sudo = self.env.sudo()
        # FIXME: search should allow many2many lookup lmfao
        # FIXME: filter & mapped tools on recordset
        user_groups = env_sudo["users_access.group"].browse(
            [
                g.id
                for g in env_sudo["users_access.group"].search([])
                if g.user_ids and self.env.uid in g.user_ids.ids
            ]
        )
        model_access = env_sudo["users_access.model_access"].search(
            [
                ("model", "=", self._name),
            ]
        )

    def create(self, vals):
        self._check_access_rights("perm_create")
        return super().create(vals)

    def read(self, fields):
        self._check_access_rights("perm_read")
        return super().read(fields)

    def write(self, vals):
        self._check_access_rights("perm_write")
        return super().write(vals)

    def delete(self):
        self._check_access_rights("perm_delete")
        return super().delete()

    def search(self, *args, **kwargs):
        self._check_access_rights("perm_read")
        return super().search(*args, **kwargs)


class Group(silly.model.Model):
    """
    Group users together into groups
    """

    _name = "users_access.group"

    name = sillyorm.fields.String(required=True)

    # group members
    user_ids = sillyorm.fields.Many2many("users.user")

    # model rules that apply to this group
    rule_ids = sillyorm.fields.Many2many("users_access.rule", "users_access_join_rule_group")

    # model access records that apply to this group
    model_access_ids = sillyorm.fields.One2many("users_access.model_access", "group_id")


class Rule(silly.model.Model):
    _name = "users_access.rule"

    name = sillyorm.fields.String(required=True)

    # model this rule applies to
    model = sillyorm.fields.String(required=True)

    # extra domain applied to the models specified in the rules, records that are not contained in this domain may not be accessed
    domain = sillyorm.fields.String(length=512, required=True)

    # groups this domain applies to - if no groups are set it applies to the model globally
    group_ids = sillyorm.fields.Many2many("users_access.group", "users_access_join_rule_group")


class GroupModelAccess(silly.model.Model):
    _name = "users_access.model_access"

    name = sillyorm.fields.String(required=True)

    # model this model_access is for
    model = sillyorm.fields.String(required=True)

    # access rights - the most permissive ones will apply
    perm_create = sillyorm.fields.Boolean(required=True)
    perm_read = sillyorm.fields.Boolean(required=True)
    perm_write = sillyorm.fields.Boolean(required=True)
    perm_delete = sillyorm.fields.Boolean(required=True)

    # groups these access rights apply to - if not set they apply to everyone
    group_id = sillyorm.fields.Many2one("users_access.group")
