from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class Vehicle(BaseModel):
    id: PyObjectId = Field(default=None, alias="_id")
    registration_number: str
    model: str
    driver: PyObjectId | None

class Driver(BaseModel):
    id: PyObjectId = Field(default=None, alias="_id")
    name: str
    license_number: str