from setuptools import setup, find_packages
import os


setup(
    name="output_viewer",
    version="0.0.2",
    description="Framework for building web pages to examine output.",
    author="Sam Fries",
    author_email="fries2@llnl.gov",
    license="BSD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"
    ],
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    scripts=["scripts/view_output", "scripts/view_output.py"]
)