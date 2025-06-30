import logging
import functools
import inspect
import flask  # TODO: maybe FastAPI??
from . import globalvars

_logger = logging.getLogger(__name__)

_profile_start_hook = lambda _: None
_profile_end_hook = lambda _: None


def route(*args, with_env: bool = True, **kwargs):
    def decorator(function):
        if len(args) > 1:
            raise Exception("Route expects maximum 1 argument, which is the URL")

        @functools.wraps(function)
        def wrap(*w_args, **w_kwargs):
            _profile_start_hook(wrap)
            if with_env:
                with globalvars.registry.environment(autocommit=True) as env:
                    with env.transaction():
                        if "env" not in w_kwargs:
                            w_kwargs["env"] = env
                        ret = function(*w_args, **w_kwargs)
            else:
                ret = function(*w_args, **w_kwargs)
            _profile_end_hook(wrap)
            return ret

        wrap.original_function = function
        wrap.route_url = args[0] if len(args) == 1 else None
        wrap.route_kwargs = kwargs

        return wrap

    return decorator


# TODO: maybe it would be good if the routers got initialized in module load order


class Router:
    direct_children = []

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        if Router in cls.__bases__:
            Router.direct_children.append(cls)


def _unique(it):
    visited = set()
    for x in it:
        if x in visited:
            continue
        visited.add(x)
        yield x


def init_routers(flask_app):
    # Given a class, goes through all it's subclasses and
    # then returns only the classes that don't have any more children
    # This is used to make our inheritance mechanism work,
    # we will inherit from these classes to build our final
    # Router class
    def get_final_classes(cls):
        res = []
        # descend
        for s in cls.__subclasses__():
            res.extend(get_final_classes(s))
        # we have arrived at the end
        if len(res) == 0:
            res.append(cls)
        return res

    for cls in Router.direct_children:
        final_classes = list(_unique(get_final_classes(cls)))
        router_ext_strs = [f"{x.__module__}.{x.__name__}" for x in final_classes if x is not cls]
        if len(router_ext_strs) > 0:
            _logger.info(
                "Router %s.%s getting extended by: " + ", ".join(router_ext_strs),
                cls.__module__,
                cls.__name__,
            )

        # Build a final Router class that inherits all the other ones
        # Also create an instance of it
        final_cls = type(cls.__name__, tuple(reversed(final_classes)), {})()

        for fn_name, fn in inspect.getmembers(final_cls, inspect.ismethod):
            # Skip all functions that don't have a route decorator anywhere in the class hierachy
            if not any(
                map(
                    lambda cls: hasattr(getattr(cls, fn_name, None), "original_function"),
                    type(final_cls).mro(),
                )
            ):
                continue

            route_url = None
            route_kwargs = {}

            # reversed because we want the classes higher up in the hierachy first so we can
            # have routes lower down overwrite parameters
            for cls2 in _unique(reversed(type(final_cls).mro())):
                if not hasattr(cls2, fn_name):
                    continue
                sub_fn = getattr(cls2, fn_name)
                if sub_fn.route_url is not None:
                    route_url = sub_fn.route_url
                route_kwargs.update(sub_fn.route_kwargs)

            if route_url is None:
                raise Exception("No URL set anywhere in the route hierachy, problem!")

            if "endpoint" not in route_kwargs:
                route_kwargs["endpoint"] = f"{cls.__module__}.{cls.__name__}.{fn_name}"

            # Allow the endpoint to be accessed by the user
            setattr(getattr(cls, fn_name), "endpoint", route_kwargs["endpoint"])

            # decorate the function
            flask_app.route(route_url, **route_kwargs)(fn)
