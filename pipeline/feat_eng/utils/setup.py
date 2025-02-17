from setuptools import setup, find_packages

setup(
    name="etl_utils",  
    version="0.1",
    packages=find_packages(), 
    install_requires=[
        "pandas",
        "numpy",
        "unidecode"
    ],
    description="A package with ETL helper functions for data cleaning and processing.",
    author="Luisa Bolsoni Sousa",
    author_email="bolsoni.luisa@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
