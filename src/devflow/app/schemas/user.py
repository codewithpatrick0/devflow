from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Letters, digits, underscore and hyphen; must start and end with an
# alphanumeric character, so '_admin', 'admin-' and '---' are rejected.
USERNAME_PATTERN = r'^[a-zA-Z0-9](?:[a-zA-Z0-9_-]*[a-zA-Z0-9])?$'


class UserRegister(BaseModel):
    email: EmailStr 
    username: str = Field(min_length=3, max_length=30, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    created_at: datetime
