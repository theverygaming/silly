import sillyorm
from . import tools


class Registry(tools.ModuleExtensibleClass, sillyorm.Registry):
    pass


class Environment(tools.ModuleExtensibleClass, sillyorm.Environment):
    pass
