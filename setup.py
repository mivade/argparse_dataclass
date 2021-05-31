import re
from setuptools import setup


def get_version():
    with open("argparse_dataclass.py") as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="argparse_dataclass",
    version=get_version(),
    author="Michael V. DePalatis",
    author_email="mike@depalatis.net",
    py_modules=["argparse_dataclass"],
    include_package_data=True,
    description="Declarative CLIs with argparse and dataclasses",
    long_description=get_readme(),
    python_requires=">=3.6",
    install_requires=["dataclasses; python_version == '3.6'",],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
