import sillyorm


class Actor(sillyorm.model.Model):
    _name = "activitypub_actor"
    
    username = sillyorm.fields.String(length=255)
    
    publickey = sillyorm.fields.Text()
    privatekey = sillyorm.fields.Text()
