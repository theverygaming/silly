import sillyorm
import logging

_logger = logging.getLogger(__name__)


class Model(sillyorm.model.Model):
    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        _logger.info(
            "model init _name: '%s' _extends: '%s' _inherits: '%s'",
            cls._name,
            cls._extends,
            cls._inherits,
        )
