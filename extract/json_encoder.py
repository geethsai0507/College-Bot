import json
from pydantic import BaseModel
from pydantic.networks import HttpUrl

class PydanticEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.model_dump()
        if isinstance(o, HttpUrl):
            return str(o)
        return super().default(o)
