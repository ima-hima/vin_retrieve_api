from sqlalchemy.orm import Session

from . import schemas
from .models import Vehicle


def get_vehicle(db: Session, vin: str):
    """Return all fields for a single vehicle from the db."""
    return db.query(Vehicle).filter(Vehicle.vin == vin).first()


def create_vehicle(db: Session, vehicle: schemas.VehicleCreate):
    """Add a vehicle to the database."""
    # I'm making all lowercase and replacing spaces so field names will match
    # models.
    vehicle_correct_keys = {k.lower().replace(" ", "_"): v for k, v in vehicle.items()}
    db_vehicle = Vehicle(**vehicle_correct_keys)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def get_all_vehicles(db: Session):
    """Return all data for all rows in db."""
    return db.query(Vehicle).all()
