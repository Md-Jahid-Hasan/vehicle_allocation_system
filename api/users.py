from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from db.mongodb import MongoDB
from schemas.user import UserCreate, UserResponse
from models.users import User
from services.service import hash_password

router = APIRouter()
database_instance = MongoDB()

@router.get("/{id}", status_code=200, response_model=UserResponse)
async def get_user(id: str, db = Depends(database_instance.get_database)):
    """Get a user by id. If not found return 404"""
    user = await db['users'].find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@router.post("/create", status_code=201, response_model=UserResponse)
async def create_user(user: UserCreate, db = Depends(database_instance.get_database)):
    """Create a new user. Check before creating if user already exist if not then create a new user"""
    # prepare user data
    user.password = hash_password(user.password)
    user_data = User(name=user.name, email=user.email, password=user.password)
    user_data = user_data.model_dump()

    # check if user already exist
    is_user_exist = await db['users'].find_one({"email": user_data['email']})
    if is_user_exist:
        raise HTTPException(status_code=400, detail="User already exist")

    # create a new user
    result = await db['users'].insert_one(user_data)
    return user_data