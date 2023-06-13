from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/lookup/{vin}")
async def lookup(vin: Optional[str]=None):
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
    if len(vin) != 17:
        raise HTTPException(status_code=404, detail="Invalid VIN. VIN must be 17 characters.")
    return {"message": f"Lookup {vin}"}


@app.get("/remove")
async def remove():
    """
    Remove VIN from cache. Return True on success. False on failure. Failure
    mode is VIN doesn't exist in cache.
    """
    return {"message": "Remove"}


@app.get("/export")
async def export():
    """Export entier cache as parquet file."""
    return {"message": "Export"}
