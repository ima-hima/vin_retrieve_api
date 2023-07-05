# VIN lookup project

#### Design an API to look up VINs and return vehicle-specific data.

##### Constraints

1. VIN look up is done using the DOT API. 
1. Any VIN already looked up should be cached using a sqlite cache.

##### Required API endpoints

1. `lookup`, which takes a VIN and returns
    a. on success, json with six fields:
      1. Input VIN Requested (string, exactly 17 alphanumeric characters)
      1. Make (String)
      1. Model (String)
      1. Model Year (String)
      1. Body Class (String)
      1. Cached Result? (Boolean);

    b. on failure (of which there are various), an http response of 404 with error message.
1. `remove`, which takes a VIN and removes it, if possible, from the cache, returning
    • on success, `True`;
    • on failure (if the id is not in the cache), `False`.
1. `export`, which returns a parquet file of all the vehicles currently in the cache.


##### Notes and design choices

1. The most difficult task was dealing with the parquet download. I attempted for quite a while to stream it, but was unable to and settled on the second-best solution, which is to write a file to /tmp, download it, then remove the file. This will not be scalable, but I ran out of time.
1. Likewise, I had intended to deploy this using Docker, but have not, due to time constraints.
1. I was unable to conceive of a nice way of testing `export`, so there is no testing of that endpoint. Otherwise, all endpoints and their failure modes should have good test coverage.
1. As far as I can tell, `fastapi` seems to do input sanitization automatically, so I didn't worry about that with either `remove` or `lookup`.
1. I use Conda and it installed Python 3.8.5 by default, thus I didn't use any of the nicer type hinting available in 3.10, but otherwise this entire project should be forward-compatible.
1. All of the code has been run through `black` and `isort`. `mypy` had a bunch of grumbles about type stub libraries being missing, but otherwise gave no complaints.
1. I did not include a `requirements-dev.txt`, as I didn't think it was necessary.


##### Installing the project
To run the project locally, set up virtual environment of your choice. This is running locally on my machine using Python 3.8.5.
`git clone`
`cd /vin_retrieve_api`
`pip install -r requirements.txt`

At this point you can run `pytest`:
`pytest vin_app tests`

To run the server, first create the db table with `alembic`, then run `uvicorn`.
`alembic upgrade head`
`uvicorn vin_app.main:app --reload`
