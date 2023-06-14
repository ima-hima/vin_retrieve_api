# VIN lookup project

#### Design an API to look up VINs

##### Constraints


##### Required API endpoints

1. `lookup`, which takes a VIN and returns
    a. on success, json with six fields:
      1. Input VIN Requested (string, exactly 17 alphanumeric characters)
      1. Make (String)
      1. Model (String)
      1. Model Year (String)
      1. Body Class (String)
      1. Cached Result? (Boolean);

    b. on failure (of which there are various), and http response of 404 with error message.
1. `remove`, which takes a VIN and removes it, if possible, from the cache, returning
    • on success, True;
    • on failure (if the id is not in the cache), False.
1. `export`, which returns a parquet file of all the vehicles currently in the cache.


##### Notes and design choices



##### Running the project

