import sillyorm
from silly import globalvars


def silly_env() -> sillyorm.Environment:
    with globalvars.registry.environment() as env:
        with env.transaction():
            yield env
