from pydantic import BaseModel

class ExampleDTO(BaseModel):
    name: str
    url: str
    location: str
