# Task 3
## Errors and Fixes

## error 1: 

- ERROR: test_find_unique_number_between_dates_with_diameter (tests.test_neo_database.TestNEOSearchUseCases)
AttributeError: 'NearEarthObject' object has no attribute 'diameter_min_km'

## Fixed
I just needed to rename an attribute in NearEarthObject model to `diameter_min_km`


## error 2: 
- ERROR: test_find_unique_number_between_dates_with_diameter_and_hazardous_and_distance (tests.test_neo_database.TestNEOSearchUseCases)

AttributeError: 'OrbitPath' object has no attribute 'neo_name'

## Fixed
I just needed to rename an attribute `name` in OrbitPath to `neo_name`
