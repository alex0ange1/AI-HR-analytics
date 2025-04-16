from pydantic import BaseModel, Field, ConfigDict


class UserRegisterCreateUpdateSchema(BaseModel):
    email: str = Field(pattern=r"^\S+@\S+\.\S+$", examples=["email@mail.ru"])
    password: str


class UserRegisterSchema(UserRegisterCreateUpdateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
