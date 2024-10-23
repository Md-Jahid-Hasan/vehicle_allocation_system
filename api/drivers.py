from fastapi import APIRouter, Depends
from bson import ObjectId
from db.mongodb import MongoDB
from models.vehicle import Driver
from schemas.vehicle import DriverCreate

router = APIRouter()
database_instance = MongoDB()

@router.get("/", status_code=200, response_model=list[Driver])
async def get_drivers(page: int = 1, db = Depends(database_instance.get_database)):
    skip = 10 * (page - 1)
    drivers = await db['drivers'].find().skip(skip).limit(10).to_list(10)
    return drivers

@router.post("/add", status_code=201)
async def add_driver(driver: DriverCreate, db = Depends(database_instance.get_database)):
    driver = driver.model_dump()
    # check if driver already exists with the same license number
    license_number = driver['license_number']
    is_driver_exists = await db['drivers'].find_one({"license_number": license_number})
    if is_driver_exists:
        return {"message": "Driver with this license number already exists"}

    # create a new driver
    result = db['drivers'].insert_one(driver)
    return {"message": "Driver added successfully"}

@router.get("/unassign/{driver_id}", status_code=200)
async def unassign_driver(driver_id:str, db = Depends(database_instance.get_database)):
    # check if id is valid
    if not ObjectId.is_valid(driver_id):
        return {"message": "Invalid driver id"}

    # retrieve a driver by id
    driver = await db['drivers'].find_one({"_id": ObjectId(driver_id)})
    if not driver:
        return {"message": "Driver not found"}

    # unassign the driver from vehicle
    result = await db['vehicles'].update_one({"driver": ObjectId(driver_id)}, {"$set": {"driver": None}})
    return {"message": "Driver unassigned successfully"}
