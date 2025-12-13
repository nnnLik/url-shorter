from typing import Any, TypeVar

import msgspec
from fastapi import Request
from fastapi.routing import JSONResponse
from fastapi.exceptions import RequestValidationError

T = TypeVar("T", bound=msgspec.Struct)


class MsgSpecJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)


async def decode_msgspec(request: Request, model: type[T]) -> T:
    body = await request.body()
    try:
        return msgspec.json.decode(body, type=model)
    except msgspec.DecodeError as e:
        raise RequestValidationError(errors=[{"type": "value_error", "msg": str(e)}])
