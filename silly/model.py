import sillyorm
import logging

_logger = logging.getLogger(__name__)

models_to_register = []


class Model(sillyorm.model.Model):
    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        # we don't register that
        if not cls._name:
            _logger.debug(
                "not registering model class '%s' (missing _name)",
                repr(cls),
            )
            return
        log_msg = "adding model to registration list: '%s'"
        log_args = [cls._name]
        if cls._extends:
            log_msg += " -- _extends: %s"
            log_args.append(cls._extends)
        if cls._inherits:
            log_msg += " -- _inherits: %s"
            log_args.append(", ".join(cls._inherits))
        _logger.debug(
            log_msg,
            *log_args,
        )
        # FIXME: should probably be removed? idk lol
        if cls in models_to_register:
            raise Exception("already registered")
        models_to_register.append(cls)
