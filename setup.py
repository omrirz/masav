import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="masav",
    version="0.0.2",
    author="Omri Rozenzaft",
    author_email="omrirz@gmail.com",
    description="Python API for Israeli Masav payments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omrirz/masav",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)