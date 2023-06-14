from sqlalchemy.orm import Session

from . import models, schemas


def get_vehicle(db: Session, vin: str):
    return db.query(models.Vehicle).filter(models.Vehicle.vin == vin).first()


def create_vehicle(db: Session, vehicle: schemas.VehicleCreate):
    db_vehicle = models.Vehicle(**vehicle)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def get_all_vehicles(db: Session):
    return db.query(models.Vehicle).all()
