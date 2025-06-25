import json
import traceback
import sillyorm
from flask import request
from silly.globalvars import env, env_lock
from silly import http

# Standard JSON-RPC errros
JSONRPC_ERROR_STD = {
    "parseError": {
        "code": -32700,
        "message": "Parse error",
    },
    "invalidRequest": {
        "code": -32600,
        "message": "Invalid Request",
    },
    "methodNotFound": {
        "code": -32601,
        "message": "Method not found",
    },
    "invalidParams": {
        "code": -32602,
        "message": "Invalid params",
    },
    "internalError": {
        "code": -32603,
        "message": "Internal error",
    },
}


class JSONRPCRoutes(http.Router):
    def jsonrpc_error(self, code, message, req_id=None):
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message,
            },
            "id": req_id,
        }

    def jsonrpc_run(self, req):
        # Verify JSON
        if not (
            # req should be a dict
            isinstance(req, dict)
            # version must match
            and req.get("jsonrpc") == "2.0"
            # id field is optional and must be null or integer
            and isinstance(req.get("id"), (type(None), int))
            # method field is required and must be a string
            and isinstance(req.get("method"), str)
            # params is optional, but if specified can only be a dict or list
            and ("params" not in req or isinstance(req.get("params"), (dict, list)))
        ):
            req_id = None
            if isinstance(req, dict):
                req_id = req.get("id")
            return self.jsonrpc_error(**JSONRPC_ERROR_STD["invalidRequest"], req_id=req_id)

        rpc_id = req.get("id")
        rpc_method = req["method"]
        rpc_params = req["params"] or []
        # FIXME: notifications return stuff atm! They shouldn't lmao

        if rpc_method not in ["env_exec", "env_exec_ids"]:
            return self.jsonrpc_error(**JSONRPC_ERROR_STD["methodNotFound"], req_id=rpc_id)

        if not isinstance(rpc_params, dict):
            return self.jsonrpc_error(**JSONRPC_ERROR_STD["invalidParams"], req_id=rpc_id)

        env_lock.acquire()
        try:
            if not (
                isinstance(rpc_params.get("model"), str)
                and isinstance(rpc_params.get("fn"), str)
                and isinstance(rpc_params.get("args", []), list)
                and isinstance(rpc_params.get("kwargs", {}), dict)
            ):
                return self.jsonrpc_error(**JSONRPC_ERROR_STD["invalidParams"], req_id=rpc_id)
            res = None
            match rpc_method:
                case "env_exec":
                    res = getattr(env[rpc_params["model"]], rpc_params["fn"])(
                        *rpc_params.get("args", []), **rpc_params.get("kwargs", {})
                    )
                case "env_exec_ids":
                    if not (isinstance(rpc_params.get("ids", []), list)):
                        return self.jsonrpc_error(
                            **JSONRPC_ERROR_STD["invalidParams"], req_id=rpc_id
                        )
                    res = getattr(
                        env[rpc_params["model"]].browse(rpc_params["ids"]), rpc_params["fn"]
                    )(*rpc_params.get("args", []), **rpc_params.get("kwargs", {}))

            if isinstance(res, sillyorm.model.Model):
                res = {
                    "objtype": "sillyModel",
                    "model": res._name,
                    "ids": res._ids,
                }

            # output JSON serializable? No? repr!
            try:
                json.dumps(res)
            except:
                res = repr(res)

            return {
                "jsonrpc": "2.0",
                "result": res,
                "id": rpc_id,
            }
        except Exception as e:
            return self.jsonrpc_error(code=-32000, message=traceback.format_exc(), req_id=rpc_id)
        finally:
            env_lock.release()

    @http.route("/api/jsonrpc", methods=["POST"])
    def jsonrpc(self):
        try:
            rdata = json.loads(request.data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.jsonrpc_error(**JSONRPC_ERROR_STD["parseError"])

        if isinstance(rdata, dict):
            return self.jsonrpc_run(rdata)
        elif isinstance(rdata, list) and len(rdata) != 0:
            ret = []
            for req in rdata:
                res = self.jsonrpc_run(req)
                if res is not None:
                    ret.append(res)
            return ret
        else:
            return self.jsonrpc_error(**JSONRPC_ERROR_STD["invalidRequest"])
