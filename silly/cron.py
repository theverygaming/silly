import logging
import asyncio
import time
import inspect
import traceback
from . import globalvars

_logger = logging.getLogger(__name__)

_all_jobs = []


def job(interval: float, with_env=False):
    def decorator(function):
        if not inspect.iscoroutinefunction(function):
            raise Exception(f"non-async function added to cron - {function}")
        _all_jobs.append(
            {
                "function": function,
                "interval": interval,
                "with_env": with_env,
            }
        )
        return function

    return decorator


async def run_jobs(shutdown_event):
    async def run_job(job):
        try:
            if job["with_env"]:
                with globalvars.registry.environment() as env:
                    with env.transaction():
                        await job["function"](env)
            else:
                await job["function"]()
        except:
            _logger.error(traceback.format_exc())

    jobs = [j | {"lastcall": time.time()} for j in _all_jobs]
    while True:
        if shutdown_event.is_set():
            return

        # round-robin through tasks we can run
        runnable = filter(
            lambda x: time.time() - x[1]["lastcall"] >= x[1]["interval"], enumerate(jobs)
        )
        for i, j in runnable:
            if shutdown_event.is_set():
                return
            j["lastcall"] = time.time()
            await run_job(j)

        # can we wait? if yes, how long?
        t_min_wait = min([j["interval"] - (time.time() - j["lastcall"]) for j in jobs])
        if t_min_wait > 0:
            await asyncio.sleep(t_min_wait)
