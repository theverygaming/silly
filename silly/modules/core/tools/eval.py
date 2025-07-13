import logging

_logger = logging.getLogger(__name__)


# FIXME: we do kinda want a safer eval
def horribly_unsafe_eval(expr, vars):
    try:
        ret = eval(expr, {}, vars)
    except Exception as e:
        _logger.error(
            "Error evalutating %s - available vars: %s", repr(expr), repr(vars), exc_info=True
        )
        raise e
    return ret
