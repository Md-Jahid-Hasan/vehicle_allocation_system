from pydantic import BaseModel

class VehicleCreate(BaseModel):
    registration_number: str
    model: str
    driver: str | None

class DriverCreate(BaseModel):
    name: str
    license_number: str