# Citibike

A pipeline, and associated tooling, for ingesting [Citibike trip data](https://s3.amazonaws.com/tripdata/index.html) and incrementally calculating the most frequently used routes.


## Getting Started

Depending on your preferred toolset, there are a couple of ways to get started.

### Docker

The simplest way to get started is with Docker. If you have Docker and Docker Compose installed on your machine, you can simply run `docker-compose up`. This will start a postgres container that is accessible at `0.0.0.0:5432` with username `citibike` and password `citibike`. Then a second container will populate the database as per the instructions.

### Python

Alternatively, if you have an existing postgres database, you can use Python. The project is tested against Python `3.6.5` but should be expected to work reasonably well with Python `3.5+`. First update `DEFAULT_URI` in [citibike/pipeline.py](citibike/pipeline.py) and `sqlalchemy.url` in [alembic.ini](alembic.ini) to your preferred URI, then run `make install`, followed by `make run`.

NOTE: depending on your system, you may need to install GNU make.


## Layout

### Citibike

The [citibike](citibike/) directory contains code for the Python module of the same name. In particular, [citibike/models.py](citibike/models.py) contains SQLalchemy models that define any tables used. Though these definitions are not explicitly used in the module, they are useful for managing table creation and future schema changes. The remaining code is contained in [citibike/pipeline.py](citibike/pipeline.py). One thing to note is that the database does all the heavy lifting. We could iterate over trips and use `collections.Counter` to track the most used routes, but a query is much more efficient.

### Migrations

The [migrations](migrations/) directory contains `alembic` database migrations. These allow us to easily change schema in the future, should the need arise.

### Tests

The [tests](tests/) directory contains tests for [citibike](citibike/). Currently there is a single integration test which tests the core `most_used_routes` update logic. You can run the tests with `make test`.


## Next Steps

In the spirit of transparency, below are some further improvements that could be made,

* The start and end timestamps are currently stored as strings. If we want to query by time ranges, we should convert them to proper timestamps.
* All of the data transformation is handled in the postgres `COPY` statement. If we want to do something more complex, we should add a `transform_trips` function.
* Loading each data file is single threaded. We should be able to parallelize this.
