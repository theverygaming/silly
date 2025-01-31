import sillyorm


class Setting(sillyorm.model.Model):
    _name = "settings_setting"

    key = sillyorm.fields.String(length=255)
    value = sillyorm.fields.Text()

    def _check_key_exists(self, key):
        res = self.search([("key", "=", key)])
        return len(res) != 0

    def write(self, vals):
        # there so no option to have unique fields, so we need to check manually for now
        if "key" in vals and self.key != vals["key"] and self._check_key_exists(vals["key"]):
            raise Exception(f"settings key {vals['key']} already exists")
        return super().write(vals)

    def create(self, vals):
        # there so no option to have unique fields, so we need to check manually for now
        if "key" not in vals:
            raise Exception("Key must be set")
        if self._check_key_exists(vals["key"]):
            raise Exception(f"settings key {vals['key']} already exists")
        return super().create(vals)

    def set_value(self, key, value):
        res = self.search([("key", "=", key)])
        if len(res) > 1:
            raise Exception(f"duplicate settings key {key}")
        if len(res) == 0:
            self.create({
                "key": key,
                "value": value,
            })
        res.value = value

    def get_value(self, key, default=None):
        res = self.search([("key", "=", key)])
        if len(res) > 1:
            raise Exception(f"duplicate settings key {key}")  # this should technically be impossible
        if len(res) == 0:
            return default
        return res.value
