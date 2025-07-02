import sys
import time
from silly import http

# TODO: fix this shit lmao, it barely works

# list of tuples # FIXME: not true anymore
# (timestamp (nanoseconds), type, filename, line, fnname)
_profile_data = {}

_profile_action = None


def _trace(frame, event, arg):
    if _profile_action not in _profile_data:
        return
    if event == "call":
        t = "O"
    elif event == "return":
        t = "C"
    else:
        return
    _profile_data[_profile_action]["data"].append(
        (
            int(time.perf_counter() * 1e9),  # timestamp
            t,  # type
            frame.f_code.co_filename,  # filename
            frame.f_code.co_firstlineno,  # line
            frame.f_code.co_name,  # fnname
        )
    )


def _http_profile_start(wrap):
    global _profile_action
    _profile_action = f"{wrap.route_url} - {int(time.perf_counter() * 1e9)}"
    _profile_data[_profile_action] = {}
    _profile_data[_profile_action]["data"] = []
    _profile_data[_profile_action]["start"] = int(time.perf_counter() * 1e9)
    sys.setprofile(_trace)


def _http_profile_end(wrap):
    sys.setprofile(None)
    if _profile_action:
        _profile_data[_profile_action]["end"] = int(time.perf_counter() * 1e9)


class Routes(http.Router):
    @http.route("/debug/profiler/start", with_env=False)
    def start(self):
        _profile_data.clear()
        http._profile_start_hook = _http_profile_start
        http._profile_end_hook = _http_profile_end
        return "started"

    @http.route("/debug/profiler/stop", with_env=False)
    def stop(self):
        http._profile_start_hook = lambda _: None
        http._profile_end_hook = lambda _: None
        return "stopped"

    @http.route("/debug/profiler/speedscope/data/<idx>", with_env=False)
    def speedscope_data(self, idx):
        def _get_data_for(key):
            events = []
            frames = []
            framecache = {}

            while _profile_data[key]["data"][0][1] == "C":
                _profile_data[key]["data"].pop(0)

            while _profile_data[key]["data"][-1][1] == "O":
                _profile_data[key]["data"].pop(-1)

            for timestamp, t, filename, line, fnname in _profile_data[key]["data"]:
                k = (filename, line, fnname)
                if k not in framecache:
                    framecache[k] = len(frames)
                    frames.append({"name": fnname, "file": filename, "line": line, "col": 1})
                frame_index = framecache[k]
                events.append({"type": t, "at": timestamp, "frame": frame_index})

            return {
                "$schema": "https://www.speedscope.app/file-format-schema.json",
                "profiles": [
                    {
                        "type": "evented",
                        "name": "python",
                        "unit": "nanoseconds",
                        "startValue": _profile_data[key]["start"],
                        "endValue": _profile_data[key]["end"],
                        "events": events,
                    }
                ],
                "shared": {"frames": frames},
                "activeProfileIndex": 0,
                "exporter": "silly",
                "name": "silly",
            }

        return _get_data_for(list(sorted(_profile_data.keys()))[int(idx)])

    @http.route("/debug/profiler/speedscope/<idx>")
    def speedscope_idx(self, env, idx):
        [[x, i] for i, x in enumerate(sorted(_profile_data.keys()))]
        return env["template"].render(
            "profiler.speedscope",
            {"profile_url": f"/debug/profiler/speedscope/data/{idx}"},
        )

    @http.route("/debug/profiler/speedscope/")
    def speedscope(self, env):
        return env["template"].render(
            "profiler.speedscope",
            {
                "profile_url": None,
                "profiles": [
                    [x, f"/debug/profiler/speedscope/{i}"]
                    for i, x in enumerate(sorted(_profile_data.keys()))
                ],
            },
        )
