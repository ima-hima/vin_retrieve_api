from typing import List, Union

from pydantic import BaseModel


class VehicleBase(BaseModel):
    title: str
    description: Union[str, None] = None


class VehicleCreate(ItemBase):
    pass


class Vehicle(ItemBase):
    vin: str
    make: str
    model: str
    model_year: int
    body_class: str

    class Config:
        orm_mode = True

