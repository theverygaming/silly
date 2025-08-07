import sillyorm
import silly


class AObject(silly.model.Model):
    isRemote = sillyorm.fields.Integer()  # TODO: boolean


class Actor(silly.model.Model):
    _name = "activitypub.actor"

    # fields from activitypub Object
    isRemote = sillyorm.fields.Integer()  # TODO: boolean

    # actor fields

    username = sillyorm.fields.String(length=255)

    publickey = sillyorm.fields.Text()
    privatekey = sillyorm.fields.Text()

    def gen_webfinger_json(self):
        return {
            "subject": f"acct:{self.username}@vps-old.infra.theverygaming.furrypri.de",
            "aliases": [],
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": (
                        f"https://vps-old.infra.theverygaming.furrypri.de/users/{self.username}"
                    ),
                }
            ],
        }

    def gen_actor_json(self):
        return {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": f"https://vps-old.infra.theverygaming.furrypri.de/users/{self.username}",
            "type": "Person",
            "preferredUsername": self.username,
            "inbox": f"https://vps-old.infra.theverygaming.furrypri.de/users/{self.username}/inbox",
            "publicKey": {
                "id": f"https://vps-old.infra.theverygaming.furrypri.de/users/{self.username}#key",
                "owner": f"https://vps-old.infra.theverygaming.furrypri.de/users/{self.username}",
                "publicKeyPem": self.publickey,
            },
            # optional
            "summary": "<p>bites u</p>hehe",
            "name": "meow!! :3",
            "attachment": [
                {"name": "tehee", "type": "PropertyValue", "value": ":3"},
                {"name": "ehehehehe,,,", "type": "PropertyValue", "value": ",,,,,"},
            ],
            "icon": {
                "mediaType": "image/jpeg",
                "type": "Image",
                "url": "https://upload.wikimedia.org/wikipedia/commons/9/9c/Fennec_Fox.jpg",
            },
        }
