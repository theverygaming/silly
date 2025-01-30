import sillyorm

class TestModel(sillyorm.model.Model):
    _name = "test_model"

    integer = sillyorm.fields.Integer()
    float = sillyorm.fields.Float()
    string = sillyorm.fields.String(length=255)
    text = sillyorm.fields.Text()
    date = sillyorm.fields.Date()
    datetime = sillyorm.fields.Datetime()
    boolean = sillyorm.fields.Boolean()
    selection = sillyorm.fields.Selection(["option 1", "option 2"])
    # TODO: many2one and one2many
