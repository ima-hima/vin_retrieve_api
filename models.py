from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    vin = Column(String, primary_key=True, index=True)
    make = Column(String)
    model = Column(String)
    model_year = Column(Integer)
    body_class = Column(String)
