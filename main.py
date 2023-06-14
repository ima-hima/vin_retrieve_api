from typing import Optional

import json
import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    raise HTTPException(
        status_code=404, detail="Appropriate endpoints are lookup, remove, export."
    )


@app.get("/lookup/{vin}")
def lookup(vin: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Look up VIN. Return json with following fields:

    Input VIN Requested (string, exactly 17 alphanumeric characters)
    Make (String)
    Model (String)
    Model Year (String)
    Body Class (String)
    Cached Result? (Boolean)

    If VIN is invalid, return 404 error.
    """
    if vin and len(vin) != 17:
        raise HTTPException(
            status_code=404, detail="Invalid VIN. VIN must be 17 characters."
        )
    # First, check to see if vin is in cache.
    vehicle_details_from_cache = crud.get_vehicle(db, vin)
    if vehicle_details_from_cache is None:
        # VIN isn't in cache, so get details from dot.gov.
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
        r = requests.get(url=url)
        desired_variables = set(
            [
                "Make",
                "Model",
                "Model Year",
                "Body Class",
                "Error Code",
                "Error Text",
                "Additional Error Text",
            ]
        )
        # Note here that I'm forced to change names of keys so they play well
        # with the database.
        vehicle_details = {
            item["Variable"]: item["Value"]
            for item in r.json()["Results"]
            if item["Variable"] in desired_variables
        }
        vehicle_details["vin"] = vin
        if vehicle_details["Error Code"] == "1":
            # There's some error. Likely nonexistent VIN.
            error_message = f"{vin} {vehicle_details['Error Text']}"
            if vehicle_details["Additional Error Text"]:
                error_message += f"{vehicle_details['Additional Error Text']}"
            raise HTTPException(status_code=404, detail=error_message)
        else:
            # Have to delete these or db insert won't work.
            del vehicle_details["Error Code"]
            del vehicle_details["Error Text"]
            del vehicle_details["Additional Error Text"]
        crud.create_vehicle(db, vehicle_details)
        vehicle_details["Cached Result?"] = False
    else:
        # The result was in the cache.
        # The following ugliness because I couldn't figure out how to get fastapi
        # db models to convert to dicts. I thought it would work throuth the
        # .dict() method of Pydantic, but no.
        vehicle_details = {
            "Make": vehicle_details_from_cache.make,
            "Model": vehicle_details_from_cache.model,
            "Model Year": vehicle_details_from_cache.model_year,
            "Body Class": vehicle_details_from_cache.body_class,
            "Cached Result?": True,
        }

    res = {k.replace("_", " ").title(): v for k, v in vehicle_details.items() if k != "vin"}
    res["VIN"] = vin
    return JSONResponse(content=res)


@app.delete("/remove/{vin}")
def remove(vin: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Remove VIN from cache. Return True on success. False on failure. Failure
    mode is VIN doesn't exist in cache.
    """
    if vin and len(vin) != 17:
        raise HTTPException(
            status_code=404, detail="Invalid VIN. VIN must be 17 characters."
        )
    vehicle = crud.get_vehicle(db, vin)
    if vehicle is None:
        return JSONResponse({"Success": False})

    db.delete(vehicle)
    db.commit()

    return JSONResponse({"Success": True})


@app.get("/export")
def export():
    """Export entier cache as parquet file."""
    return {"msg": "Export"}
