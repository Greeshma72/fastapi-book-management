from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

class User(BaseModel):
    username: str
    email: str
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True
