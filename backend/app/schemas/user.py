from pydantic import BaseModel, ConfigDict, EmailStr, UUID4

from app.models.user import UserRole


class OrgCreate(BaseModel):
    name: str
    slug: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    org_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    email: str
    full_name: str | None
    role: UserRole
    org_id: UUID4


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
