import json
from typing import Any

def json_response(status: str, data: dict | None = None, error_msg: str | None = None) -> str:
    payload = {"status": status}
    if data is not None:
        payload["data"] = data
    if error_msg:
        payload["error_msg"] = error_msg
    return json.dumps(payload, ensure_ascii=False, indent=2)
