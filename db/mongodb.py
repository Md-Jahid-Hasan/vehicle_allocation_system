from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings


class MongoDB:
    """This class is responsible for handling MongoDB connection and database operations. It is a singleton class,
    so only one instance of this class will be created and shared across the application."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MongoDB, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, uri: str = settings.DATABASE_URL, db_name: str = settings.DATABASE_NAME):
        if not hasattr(self, 'initialized'):
            print("Initializing MongoDB")
            self.client = None
            self.db_name = db_name
            self.uri = uri

    async def connect(self):
        self.client = AsyncIOMotorClient(self.uri)
        print("Connected to MongoDB")

    async def close(self):
        if self.client:
            self.client.close()
            self._instance = None
            print("Disconnected from MongoDB")

    def get_database(self):
        return self.client.get_database('transport_management')
