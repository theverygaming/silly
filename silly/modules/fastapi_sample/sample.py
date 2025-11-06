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


class Person(pydantic.BaseModel):
    name: str
    age: int


@sample_router.post("/person")
async def create_person(
    env: Annotated[sillyorm.Environment, fastapi.Depends(silly_env)], person: Person
) -> str:
    env["fastapi_sample.person"].create(person.dict())
    return person.name


@sample_router.get("/person")
async def get_person(
    env: Annotated[sillyorm.Environment, fastapi.Depends(silly_env)], name: str
) -> Person | None:
    p = env["fastapi_sample.person"].search([("name", "=", name)])
    if not p:
        return
    return Person(**p.read(["name", "age"])[0])


@sample_router.delete("/person")
async def delete_person(
    env: Annotated[sillyorm.Environment, fastapi.Depends(silly_env)], name: str
) -> Person | None:
    p = env["fastapi_sample.person"].search([("name", "=", name)])
    if not p:
        return
    vals = p.read(["name", "age"])[0]
    p.delete()
    return Person(**vals)
