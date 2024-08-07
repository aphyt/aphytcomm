import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aphyt",
    version="0.1.22",
    author="Joseph Ryan",
    author_email="jr@aphyt.com",
    description="A library to communicate with Omron NX and NJ PLC and motion controllers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aphyt/aphytcomm",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"aphyt.tkmi": ["Transparent_Pixel.png"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
