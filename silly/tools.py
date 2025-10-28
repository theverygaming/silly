def get_final_classes(cls):
    """
    Given a class, goes through all it's subclasses and
    then returns only the classes that don't have any more children

    This can be used to make classes inheritable by modules,
    you inherit from these classes to build a final class
    """
    res = []
    # descend
    for c in cls.__subclasses__():
        res.extend(get_final_classes(c))
    # we have arrived at the end
    if len(res) == 0:
        res.append(cls)
    return res


def unique(it):
    """
    Generator that takes an iterable as input and then only returns unique elements.

    Order is guranteed
    """
    visited = set()
    for x in it:
        if x in visited:
            continue
        visited.add(x)
        yield x


class ModuleExtensibleClass:
    @classmethod
    def module_extensible_get_final_extended_class(cls):
        final_classes = list(unique(get_final_classes(cls)))
        return type(cls.__name__, tuple(reversed(final_classes)), {})
