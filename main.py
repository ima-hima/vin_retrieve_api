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
    vehicle_details = crud.get_vehicle(db, vin)

    if vehicle_details is None:
        # VIN isn't in cache, so get details from dot.gov.
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
        r = requests.get(url=url)
        desired_variables = set(["Make", "Model", "Model Year", "Body Class", "Error Code", "Error Text", "Additional Error Text",])
        # Note here that I'm forced to change names of keys so they play well
        # with the database.
        vehicle_details = {item["Variable"].lower().replace(" ", "_"): item["Value"] for item in r.json()["Results"] if item["Variable"] in desired_variables}
        vehicle_details["vin"] = vin

        if vehicle_details["error_code"] == "1":
            error_message = f"{vin} {vehicle_details['error_text']}"
            if vehicle_details['additional_error_text']:
                error_message += f"{vehicle_details['additional_error_text']}"
            raise HTTPException(status_code=404, detail=error_message)
        else:
            # Have to delete these or db insert won't work.
            del vehicle_details["error_code"]
            del vehicle_details["error_text"]
            del vehicle_details["additional_error_text"]
        crud.create_vehicle(db, vehicle_details)
        vehicle_details["Cached Result?"] = False
    else:
        print(vehicle_details)
        vehicle_details["Cached Result?"] = True

    res = {k.replace("_", " ").title(): v for k, v in vehicle_details.items()}
    return JSONResponse(content=vehicle_details)


@app.get("/remove/{vin}")
def remove(vin: Optional[str] = None):
    """
    Remove VIN from cache. Return True on success. False on failure. Failure
    mode is VIN doesn't exist in cache.
    """
    if vin and len(vin) != 17:
        raise HTTPException(
            status_code=404, detail="Invalid VIN. VIN must be 17 characters."
        )
    return JSONResponse(content=json.loads(f"\{'VIN': {vin}, 'Cache Delete Success': False\}"))


@app.get("/export")
def export():
    """Export entier cache as parquet file."""
    return {"msg": "Export"}
