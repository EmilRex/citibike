from setuptools import find_packages, setup


setup(name="citibike",
    version="1.0.0",
    description="Extract, load and aggregate citibike trip data",
    author="Emil Christensen",
    packages=find_packages("."),
    install_requires=[
        "alembic==1.0.8",
        "psycopg2==2.7.7",
        "requests==2.32.0",
        "SQLAlchemy==1.3.1"
    ],
)
