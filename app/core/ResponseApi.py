from typing import Optional, Dict, Generic, TypeVar
from pydantic import BaseModel
from fastapi.responses import JSONResponse

T = TypeVar('T')

class ResponseAPI(BaseModel, Generic[T]):
    code: int = 200
    message: Optional[str] = None
    data: Optional[T] = None

    def __init__(self, data: Optional[T] = None, message: Optional[str] = None, code: int = 200):
        super().__init__(data=data, message=message, code=code)
        if message is not None:
            object.__setattr__(self, 'code', 400)
            object.__setattr__(self, 'message', message)

    def to_json_response(self):
        return JSONResponse(
            status_code=self.code,
            content=self.dict()
        )