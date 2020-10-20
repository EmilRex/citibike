"""Database models for citibike trip data"""
from sqlalchemy import Column, Float, Integer, MetaData, String, Table


metadata = MetaData()

def trip_fact_variant(name):
    """
    Generate a trip_fact table with the given name

    Args:
        name: name of the table

    Returns:
        a sqlalchemy.Table instance
    """
    return Table(name, metadata,
        Column("tripduration", Integer),
        Column("starttime", String),
        Column("stoptime", String),
        Column("start_station_id", Integer),
        Column("start_station_name", String, index=True),
        Column("start_station_latitude", Float),
        Column("start_station_longitude", Float),
        Column("end_station_id", Integer),
        Column("end_station_name", String, index=True),
        Column("end_station_latitude", Float),
        Column("end_station_longitude", Float),
        Column("bikeid", String),
        Column("usertype", String),
        Column("birth_year", Integer),
        Column("gender", Integer)
    )

def most_used_routes_variant(name):
    """
    Generate a most_used_routes table with the given name

    Args:
        name: name of the table

    Returns:
        a sqlalchemy.Table instance
    """
    return Table(name, metadata,
        Column("route_id", String, primary_key=True),
        Column("start_station_name", String, index=True),
        Column("end_station_name", String, index=True),
        Column("num_trips", Integer)
    )

trip_fact = trip_fact_variant("trip_fact")
trip_fact_stg = trip_fact_variant("trip_fact_stg")
most_used_routes = most_used_routes_variant("most_used_routes")
