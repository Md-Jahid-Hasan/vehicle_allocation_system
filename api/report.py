from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request
from bson import ObjectId
from db.mongodb import MongoDB

router = APIRouter()
database_instance = MongoDB()

@router.get("/vehicle/{vehicle_id}/", status_code=200)
async def get_vehicles_allocation_report(vehicle_id: str, request: Request, db = Depends(database_instance.get_database)):
    """Get vehicle allocation report by vehicle id and number of days, number of days pass in query params as *days*. It return
    in last x number of days how many times vehicle is allocated user"""
    if not ObjectId.is_valid(vehicle_id):
        return {"message": "Invalid vehicle id"}

    query_params = dict(request.query_params)
    number_of_days = query_params.get('days', 7)

    current_date = datetime.now().date()
    query_date = current_date - timedelta(days=int(number_of_days))

    vehicle_allocation = await db["allocation"].count_documents({"vehicle": ObjectId(vehicle_id), "date": {
            "$gte": query_date.strftime("%Y-%m-%d"),
            "$lte": current_date.strftime("%Y-%m-%d")
        }})

    return {"allocation": vehicle_allocation}


@router.get("/user/{user_id}/", status_code=200)
async def get_vehicles_allocation_report(user_id: str, request: Request, db = Depends(database_instance.get_database)):
    """Get user allocation report by user id and number of days, number of days pass in query params as *days*. It return
    in last x number of days how many times user is allocated a vehicle"""
    if not ObjectId.is_valid(user_id):
        return {"message": "Invalid vehicle id"}

    query_params = dict(request.query_params)
    number_of_days = query_params.get('days', 7)

    current_date = datetime.now().date()
    query_date = current_date - timedelta(days=int(number_of_days))

    vehicle_allocation = await db["allocation"].count_documents({
        "user": ObjectId(user_id),
        "date": {
            "$gte": query_date.strftime("%Y-%m-%d"),
            "$lte": current_date.strftime("%Y-%m-%d")
        }
    })

    return {"allocation": vehicle_allocation}