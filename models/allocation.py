from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated
from datetime import date

PyObjectId = Annotated[str, BeforeValidator(str)]

class Allocation(BaseModel):
    user: PyObjectId = Field(default=None)
    vehicle: PyObjectId = Field(default=None)
    date: date