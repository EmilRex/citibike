"""Extracts and loads citibike trip data"""
import argparse
import io
import logging
import sys
import zipfile

import requests
import sqlalchemy


BASE_URL = "https://s3.amazonaws.com/tripdata/{year:04d}{month:02d}-citibike-tripdata.csv.zip"
BASE_FILENAME = "{year:04d}{month:02d}-citibike-tripdata.csv"
DEFAULT_URI = "postgresql+psycopg2://citibike:citibike@postgres"


def extract_trips(year, month):
    """
    Reads and decompresses trip data in memory

    Args:
        year: integer year of the desired data file
        month: integer month of the desired data file

    Returns:
        an open file handle to the csv data
    """
    url = BASE_URL.format(year=year, month=month)
    filename = BASE_FILENAME.format(year=year, month=month)

    logging.info("Retrieving '{}'".format(url))
    response = requests.get(url)
    response.raise_for_status()

    logging.info("Decompressing '{}'".format(filename))
    zf_handle = zipfile.ZipFile(io.BytesIO(response.content))
    return zf_handle.open(filename)


def load_trips(file_handle, table, engine):
    """
    Efficiently loads trip data by leveraging postgres copy

    Args:
        file_handle: an open file handle to the csv data
        table: name of the table to load to
        engine: a SQLalchemy engine instance

    Returns:
        None
    """
    statement = "COPY {table} FROM STDIN WITH CSV HEADER DELIMITER ',' NULL 'NULL' QUOTE '\"'".format(table=table)
    conn = engine.raw_connection()
    with conn.cursor() as cur:
        logging.info("Copying to '{}'".format(table))
        cur.copy_expert(statement, file_handle)
    conn.commit()


def aggregate_trips(source, target, engine):
    """
    Aggregate the number of trips in table and update most_used_routes

    Args:
        source: name of the table to aggregate from
        target: name of the table to aggregate to
        engine: a SQLalchemy engine instance

    Returns:
        None
    """
    query = """
        INSERT INTO {target}
            SELECT
                MD5(CONCAT(start_station_name, end_station_name)) AS route_id,
                start_station_name,
                end_station_name,
                COUNT(start_station_name) AS num_trips
            FROM
                {source}
            GROUP BY
                start_station_name,
                end_station_name
        ON CONFLICT (route_id) DO
        UPDATE SET num_trips = {target}.num_trips + EXCLUDED.num_trips
    """
    engine.execute(query.format(source=source, target=target))


def configure_logging():
    """
    Helper function for logging configuration
    """
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s"
    )


def parse_args(args):
    """
    Helper function for command line arguments
    """
    parser = argparse.ArgumentParser(description="Extract and load citibike trip data")
    parser.add_argument("-u", "--uri", required=False, default=DEFAULT_URI, help="Target database URI")
    return parser.parse_args(args)


def main():
    """
    Main execution entrypoint
    """
    args = parse_args(sys.argv[1:])
    configure_logging()
    engine = sqlalchemy.create_engine(args.uri)

    logging.info("Populating trip_fact with Jan-Jun data")
    # TODO: Use threading here to parallelize operation
    for month in range(1, 7):
        trips = extract_trips(2018, month)
        load_trips(trips, "trip_fact", engine)

    logging.info("Aggregating trip_fact to most_used_routes")
    aggregate_trips("trip_fact", "most_used_routes", engine)

    logging.info("Populating trip_fact_stg with July data")
    trips = extract_trips(2018, 7)
    load_trips(trips, "trip_fact_stg", engine)

    logging.info("Aggregating trip_fact_stg to most_used_routes")
    aggregate_trips("trip_fact_stg", "most_used_routes", engine)


if __name__ == '__main__':
    main()
