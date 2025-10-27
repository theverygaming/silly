from typing import Annotated
import fastapi
import pydantic
import sillyorm
from silly.modules.fastapi import routes, dependencies
from silly.modules.fastapi.dependencies import silly_env


class FastAPIRoutes(routes.FastAPIRoutes):
    def fastapi_app_defs(self):
        res = super().fastapi_app_defs()
        return res + [
            {
                "title": "FastAPI sample",
                "description": ":3",
                "mountpoint": "/fastapi_sample",
                "routers": [sample_router],
            }
        ]


sample_router = fastapi.APIRouter()


class XMLId(pydantic.BaseModel):
    xmlid: str
    model_name: str
    model_id: int
    source_module: str


@sample_router.get("/xmlids", response_model=list[XMLId])
def get_xmlids(env: Annotated[sillyorm.Environment, fastapi.Depends(silly_env)]) -> list[XMLId]:
    return [
        XMLId(**rec.read(["xmlid", "model_name", "model_id", "source_module"])[0])
        for rec in env["core.xmlid"].search([])
    ]
