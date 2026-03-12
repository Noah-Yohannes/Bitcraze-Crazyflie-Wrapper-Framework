from setuptools import setup, find_packages

setup(
    name="crazyflie_flight_framework",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)