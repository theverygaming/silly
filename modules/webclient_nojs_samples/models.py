import sillyorm
import silly


class TestModel(silly.model.Model):
    _name = "test_model"

    integer = sillyorm.fields.Integer()
    float = sillyorm.fields.Float()
    string = sillyorm.fields.String(length=255)
    text = sillyorm.fields.Text()
    date = sillyorm.fields.Date()
    datetime = sillyorm.fields.Datetime(tzinfo=None)
    boolean = sillyorm.fields.Boolean()
    selection = sillyorm.fields.Selection(["option 1", "option 2"])
    # TODO: many2one and one2many

    def action_test(self):
        x = f"action_test!! self: {self}"
        print(x)
        return {
            "type": "message",
            "message": x,
        }
