import sillyorm
import silly


class Module(silly.model.Model):
    _name = "core.module"

    name = sillyorm.fields.String(length=255)
    version = sillyorm.fields.String(length=255)
