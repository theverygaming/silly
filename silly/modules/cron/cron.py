import logging
import datetime
import traceback
import silly
import sillyorm
from silly.modules.core.tools.eval import horribly_unsafe_eval
import sqlalchemy

_logger = logging.getLogger(__name__)
_logger_runner = logging.getLogger(__name__ + ".runner")


class Cron(silly.model.Model):
    _name = "cron.job"

    # descriptive name for the job
    name = sillyorm.fields.String(required=True)

    # run interval in minutes
    interval = sillyorm.fields.Integer(required=True)

    # python to run
    code = sillyorm.fields.Text(required=True)

    # lock while the job is running
    locked = sillyorm.fields.Boolean(required=True, default=False)

    # earliest time when the job will next be executed
    next_run = sillyorm.fields.Datetime(tzinfo=datetime.timezone.utc)

    def _try_lock(self):
        self.ensure_one()
        # attempt to lock
        n_affected = self.env.connection.execute(
            sqlalchemy.update(self._table)
            .where(
                sqlalchemy.and_(
                    self._table.c.id == self.id,
                    self._table.c.locked == False,
                )
            )
            .values(locked=True)
        ).rowcount
        # could not set lock on the row? Failed!
        if n_affected != 1:
            return False
        return True

    def _unlock(self):
        self.locked = False

    def try_run(self):
        if not self._try_lock():
            return False
        try:
            _logger.info("running cron '%s'", self.name)
            self.next_run = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                minutes=self.interval
            )
            horribly_unsafe_eval(self.code, {"env": self.env, "_logger": _logger_runner})
        except:
            _logger.error("cron '%s' run failed: %s", self.name, traceback.format_exc())
            return False
        finally:
            self._unlock()
        _logger.info("cron '%s' finished", self.name)
        return True

    def run_next(self):
        crons = self.search(
            [
                ("locked", "=", False),
                "&",
                "(",
                ("next_run", "<=", datetime.datetime.now(datetime.timezone.utc)),
                "|",
                ("next_run", "=", None),
                ")",
            ]
        )
        for cron in crons:
            cron.try_run()


@silly.cron.job(30, with_env=True)
async def main_job(env):
    env["cron.job"].run_next()
