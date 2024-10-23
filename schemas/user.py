from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def check_password_match(cls, confirm_password, values) -> str:
        password = values.data.get("password")
        if password and confirm_password != password:
            raise ValueError('Passwords do not match')
        return confirm_password


class UserResponse(BaseModel):
    name: str
    email: EmailStr