from datetime import datetime

from fastapi import APIRouter, Depends, Request
from bson import ObjectId
from db.mongodb import MongoDB
from models.vehicle import Vehicle
from schemas.vehicle import VehicleCreate
from services.service import get_free_vehicle_on_given_day

router = APIRouter()
database_instance = MongoDB()

@router.get("/", status_code=200, response_model=list[Vehicle])
async def get_vehicles(page: int = 1, db = Depends(database_instance.get_database)):
    skip = 10 * (page - 1)
    vehicles = await db['vehicles'].find().skip(skip).limit(10).to_list(10)
    return vehicles

@router.get("/{id}", status_code=200, response_model=Vehicle|dict)
async def get_vehicle(id:str, db = Depends(database_instance.get_database)):
    """Get specific vehicle by vehicle id"""

    # check if id is valid
    if not ObjectId.is_valid(id):
        return {"message": "Invalid vehicle id"}

    # retrieve a vehicle by id
    vehicle = await db['vehicles'].find_one({"_id": ObjectId(id)})
    if not vehicle:
        return {"message": "Vehicle not found"}
    return vehicle

@router.post("/add", status_code=201)
async def add_vehicle(vehicle: VehicleCreate, db = Depends(database_instance.get_database)):
    """add/create a new vehicle by providing registration_number, model and driver id(Optional)"""
    vehicle = vehicle.model_dump()
    # check if vehicle already exists with the same registration number
    registration_number = vehicle['registration_number']
    is_vehicle_exists = await db['vehicles'].find_one({"registration_number": registration_number})
    if is_vehicle_exists:
        return {"message": "Vehicle with this registration number already exists"}

    # create a new vehicle
    result = db['vehicles'].insert_one(vehicle)
    return {"message": "Vehicle added successfully"}

# @router.get("/{driver_id}/{vehicle_id}", status_code=200)
@router.put("/assign_driver", status_code=200)
async def assign_driver_to_vehicle(body:dict, db = Depends(database_instance.get_database)):
    """Assign a driver to a vehicle by providing driver_id and vehicle_id. It makes sure that vehicle is not already
    assigned to a driver and driver is free to assign"""

    # checking the validity of the driver and vehicle id
    driver_id = body.get('driver_id')
    vehicle_id = body.get('vehicle_id')

    if not ObjectId.is_valid(driver_id) or not ObjectId.is_valid(vehicle_id):
        return {"message": "Invalid driver/vehicle id"}

    # looking for driver and vehicle with given id
    driver = await db['drivers'].find_one({"_id": ObjectId(driver_id)})
    vehicle = await db['vehicles'].find_one({"_id": ObjectId(vehicle_id)})

    # if driver or vehicle not found return message
    if not driver or not vehicle:
        return {"message": "Driver/Vehicle not found"}

    # if vehicle already has a driver assigned
    if vehicle.get('driver'):
        return {"message": "Vehicle already assigned to a driver"}

    # check if driver is free to assign
    is_driver_free = await db['vehicles'].count_documents({"driver": ObjectId(driver_id)})
    if is_driver_free != 0:
        return {"message": "Driver is not free to assign"}

    # assign driver to vehicle
    db['vehicles'].update_one({"_id": ObjectId(vehicle_id)}, {"$set": {"driver": ObjectId(driver_id)}})
    return {"message": "Driver assigned to vehicle successfully"}


@router.post("/allocate/user", status_code=200)
async def allocate_vehicle_to_user(body:dict, db = Depends(database_instance.get_database)):
    """Assign a vehicle to a user by providing user_id and vehicle_id. It makes sure that vehicle is not already
    assigned to a user."""

    # Check if the allocation date is greater than today's date
    date = body.get('date')
    date = datetime.strptime(date, "%d-%m-%Y").date()
    if date <= datetime.now().date():
        return {"message": "Allocation date should be tomorrow or later"}

    # checking the validity of the user id
    user_id = body.get('user_id')
    if not ObjectId.is_valid(user_id):
        return {"message": "Invalid data for user"}

    # looking for user with given id
    user = await db['users'].count_documents({"_id": ObjectId(user_id)})
    if not user:
        return {"message": "User not found"}

    available_vehicles = await get_free_vehicle_on_given_day(date, db)
    if not available_vehicles:
        return {"message": "No vehicle available for allocation"}
    # allocate the vehicle to user
    allocation = {"user":ObjectId(user_id), "vehicle":available_vehicles['_id'], "date":date.strftime("%Y-%m-%d")}
    result = await db['allocation'].insert_one(allocation)

    return {"message": "User assigned to vehicle successfully"}

@router.get("/allocate_update/{allocate_id}/", status_code=200)
async def update_allocation(allocate_id: str, request:Request, db = Depends(database_instance.get_database)):
    """Update allocation date, vehicle of a previous allocation by allocation id
     query_params: date, vehicle_id date format should be dd-mm-yyyy
    """
    if not ObjectId.is_valid(allocate_id):
        return {"message": "Invalid allocation id"}

    # check that is proivde a valid allocation id
    allocation = await db['allocation'].find_one({"_id": ObjectId(allocate_id)})
    if not allocation:
        return {"message": "No allocation found with this id"}

    update_set = {}
    query_params = dict(request.query_params)
    # check what is provide in the query params
    if 'date' in query_params:
        # if date exist then check if it is greater than today's date
        date = query_params.get('date')
        date = datetime.strptime(date, "%d-%m-%Y").date()
        if date <= datetime.now().date():
            return {"message": "Allocation date should be tomorrow or later"}
        update_set['date'] = date.strftime("%Y-%m-%d")

    if "vehicle" in query_params:
        # if vehicle exist in query_params then allocate a new vehicle
        vehicle = query_params.get('vehicle')
        date = datetime.strptime(allocation.get('date'), "%Y-%m-%d").date()
        available_vehicle = await get_free_vehicle_on_given_day(date, db)
        if not available_vehicle:
            return {"message": "No vehicle available for allocation"}
        update_set['vehicle'] = ObjectId(available_vehicle['_id'])

    if update_set:
        db['allocation'].update_one({"_id": ObjectId(allocate_id)}, {"$set": update_set})
    return {"message": "Allocation updated successfully"}


""" This api not properly tested. There may be a issues"""
# @router.delete("/allocate/delete/", status_code=200)
# async def cancel_allocation(request: Request, db = Depends(database_instance.get_database)):
#     """Cancel allocation of user or vehicle on a specefic date.
#     query_params: user_id or vehicle_id and date. date format should be dd-mm-yyyy"""
#     query_params = dict(request.query_params)
#     data = {}
#
#     # getting user data from the query params to ensure which allocation to delete
#     if "user_id" in query_params:
#         data["user"] = query_params.get("user_id")
#     elif "vehicle_id" in query_params:
#         data["vehicle"] = query_params.get("vehicle_id")
#     else:
#         return {"message": "No action performed"}
#
#     # verify id
#     if not ObjectId.is_valid(data[next(iter(data))]):
#         return {"message": "Invalid query params passed"}
#     data[next(iter(data))] = ObjectId(data[next(iter(data))])
#     # ensure that date is provided and date should be valid
#     date = query_params.get("date")
#     if not date:
#         return {"message": "Date is required to cancel allocation for user or vehicle"}
#
#     # check if given date is passed or not
#     date = datetime.strptime(date, "%d-%m-%Y").date()
#     if date <= datetime.now().date():
#         return {"message": "Allocation date should be tomorrow or later"}
#     data["date"] = date.strftime("%Y-%m-%d")
#
#     # cancel allocation
#     result = await db['allocation'].delete_one(data)
#     if result.deleted_count == 0:
#         return {"message": "There is no allocation for cancellation"}
#
#     return {"message": "Allocation cancelled successfully"}

@router.delete("/allocate/delete/{allocate_id}/", status_code=200)
async def cancel_allocation_by_id(allocate_id: str, db = Depends(database_instance.get_database)):
    """Cancel allocation based on allocation id"""
    if not ObjectId.is_valid(allocate_id):
        return {"message": "Invalid allocation id"}

    # check if any allocation exists with given id
    allocation = await db['allocation'].find_one({"_id": ObjectId(allocate_id)})
    if not allocation:
        return {"message": "No allocation found with this id"}

    # check if allocation date is passed or not
    allocation_date = allocation.get('date').date()
    if allocation_date <= datetime.now().date():
        return {"message": "You can't cancel this allocation. Last time to cancel is over"}
    # delete/cancel allocatioin
    result = await db['allocation'].delete_one({"_id": ObjectId(allocate_id)})

    return {"message": "Allocation cancelled successfully"}



