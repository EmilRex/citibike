import io

import pytest
import sqlalchemy

from citibike import pipeline
from citibike import models


def _csv_file(trips):
    """
    Helper function for constructing dummy csv data
    """
    header = (
        "tripduration,starttime,stoptime,start station id,"
        "start station name,start station latitude,start "
        "station longitude,end station id,end station name,"
        "end station latitude,end station longitude,bikeid,"
        "usertype,birth year,gender\n"
    )
    body = ""
    for start, end, num in trips:
        for _ in range(num):
            body += "0,NULL,NULL,0,{start},0.0,0.0,0,{end},0.0,0.0,NULL,NULL,0,0\n".format(start=start, end=end)
    return io.StringIO(header + body)


def _get_counts(engine):
    """
    Helper function for retrieving route counts
    """
    result = engine.execute("SELECT * FROM test_most_used_routes")
    return {
        (row["start_station_name"], row["end_station_name"]): row["num_trips"]
    for row in result}


@pytest.fixture(scope="session")
def first_csv():
    """
    Fixture for test_trip_fact source
    """
    trips = [
        ("A", "B", 5),
        ("B", "A", 5),
    ]
    return _csv_file(trips)


@pytest.fixture(scope="session")
def second_csv():
    """
    Fixture for test_trip_fact_stg source
    """
    trips = [
        ("A", "B", 5),
        ("C", "D", 5),
    ]
    return _csv_file(trips)


@pytest.fixture(scope="session")
def engine():
    """
    Fixture for constructing and destructing needed tables
    """
    engine = sqlalchemy.create_engine(pipeline.DEFAULT_URI)

    tables = [
        models.trip_fact_variant("test_trip_fact"),
        models.trip_fact_variant("test_trip_fact_stg"),
        models.most_used_routes_variant("test_most_used_routes")
    ]

    [table.create(engine) for table in tables]
    yield engine
    [table.drop(engine) for table in tables]


def test_aggregations(engine, first_csv, second_csv):
    """
    Test that aggregation works correctly. In particular,
        - (A, B) is counted independently of (B, A)
        - Existing pairs are updated
        - New pairs are added
    """
    pipeline.load_trips(first_csv, "test_trip_fact", engine)
    pipeline.aggregate_trips("test_trip_fact", "test_most_used_routes", engine)
    assert _get_counts(engine) == {("A", "B"): 5, ("B", "A"): 5}

    pipeline.load_trips(second_csv, "test_trip_fact_stg", engine)
    pipeline.aggregate_trips("test_trip_fact_stg", "test_most_used_routes", engine)
    assert _get_counts(engine) == {("A", "B"): 10, ("B", "A"): 5, ("C", "D"): 5}
