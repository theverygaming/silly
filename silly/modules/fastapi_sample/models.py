import sillyorm
import silly


class Person(silly.model.Model):
    _name = "fastapi_sample.person"
    name = sillyorm.fields.String(length=255, required=True, unique=True)
    age = sillyorm.fields.Integer(required=True)
