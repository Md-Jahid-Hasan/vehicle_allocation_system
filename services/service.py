from passlib.context import CryptContext
from datetime import datetime

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return hash_context.hash(password)


async def get_free_vehicle_on_given_day(date: datetime.date, db) -> dict|None:
    """
    This function will return a vehicle that is free on the given date. It will return None if no vehicle is free on that
    day.
    :param db: database instance
    :param date: which day to check for free vehicle
    :return: dict
    """
    pipeline = [
        {
            "$lookup": {
                "from": "allocation",  # The 'allocations' collection
                "localField": "_id",  # _id from 'vehicles'
                "foreignField": "vehicle",  # vehicle_id from 'allocations'
                "as": "allocation"  # Resulting array field to store allocations
            }
        },
        {
            "$match": {
                "$or": [
                    { "allocation": { "$size": 0 } },  # Match vehicles with no allocations
                    { "allocation.date": { "$ne": date.strftime("%Y-%m-%d") } }  # Exclude vehicles allocated on the specific date
                ]
            }
        },
        {"$limit": 1 },
        {
            "$project": {
                "_id": 1
            }
        }

    ]

    # check if any vehicle is available for allocation on that day
    try:
        available_vehicles = await db['vehicles'].aggregate(pipeline).next()
        print(available_vehicles)
        return available_vehicles
    except StopAsyncIteration:
        return None
