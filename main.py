from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from core.config import settings
from db.mongodb import MongoDB
from api.vehicle import router as vehicle_router
from api.users import router as user_router
from api.drivers import router as driver_router
from api.report import router as report_router
from services.custom_response import validation_exception_handler

@asynccontextmanager
async def on_startup(app: FastAPI):
    print("Connecting to Database")
    db_instance = MongoDB()
    client = await db_instance.connect()
    yield
    await db_instance.close()


app = FastAPI(title=settings.APP_NAME, lifespan=on_startup)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(vehicle_router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(driver_router, prefix="/api/drivers", tags=["driver"])
app.include_router(report_router, prefix="/api/report", tags=["report"])

@app.get("/")
async def read_root():
    return {"Hello": "World"}