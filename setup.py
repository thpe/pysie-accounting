""" package setup """
import setuptools

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysie_accounting",
    version="0.0.2",
    author="Thomas Petig",
    author_email="thomas@petig.eu",
    description="SIE file decoder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thpe/pysie-accounting",
    packages=setuptools.find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
