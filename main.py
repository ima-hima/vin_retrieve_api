from typing import Optional

import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
async def root():
    raise HTTPException(
            status_code=404, detail="Appropriate endpoints are lookup, remove, export."
        )


@app.get("/lookup/{vin}")
async def lookup(vin: Optional[str] = None):
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
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    # Note, only search public domain records. No real reason for that; I
    # just didn't change it from the example on the API usage page.
    # Also, only getting a single record on the first call because we just
    # need the number of results.
    r = requests.get(url=url)
    desired_variables = set(["Make", "Model", "Model Year", "Body Class", "Error Code", "Error Text", "Additional Error Text",])
    vehicle_details = {item["Variable"]: item["Value"] for item in r.json()["Results"] if item["Variable"] in desired_variables}
    vehicle_details["VIN"] = vin

    if vehicle_details["Error Code"] == "1":
        error_message = f"{vin} {vehicle_details['Error Text']}"
        if vehicle_details['Additional Error Text']:
            error_message += f"{vehicle_details['Additional Error Text']}"
        raise HTTPException(status_code=404, detail=error_message)

    return {"msg": f"Lookup {vehicle_details}"}


@app.get("/remove/{vin}")
async def remove(vin: Optional[str] = None):
    """
    Remove VIN from cache. Return True on success. False on failure. Failure
    mode is VIN doesn't exist in cache.
    """
    if vin and len(vin) != 17:
        raise HTTPException(
            status_code=404, detail="Invalid VIN. VIN must be 17 characters."
        )
    return {"msg": "Remove"}


@app.get("/export")
async def export():
    """Export entier cache as parquet file."""
    return {"msg": "Export"}
