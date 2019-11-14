import os
import sys

from setuptools import setup

REQUIRED_PYTHON = (3, 6)


def assert_python_version(version_info):
    current_python = version_info[:2]
    error_message = "Python {}.{} is required, but you're running Python {}.{}"
    error_message = error_message.format(*(REQUIRED_PYTHON + current_python))
    assert current_python >= REQUIRED_PYTHON, error_message


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


# exposing the params so it can be imported
setup_params = {
    "name": "mysodexo",
    "version": "20191114",
    "description": "Mysodexo Python client",
    "long_description": read("README.md"),
    "long_description_content_type": "text/markdown",
    "author": "Andre Miras",
    "url": "https://github.com/AndreMiras/mysodexo",
    "packages": ("mysodexo",),
    "install_requires": ("requests", "appdirs"),
    "include_package_data": True,
    "entry_points": {"console_scripts": ("mysodexo=mysodexo.cli:main",)},
}


def run_setup():
    assert_python_version(sys.version_info)
    setup(**setup_params)


# makes sure the setup doesn't run at import time
if __name__ == "__main__":
    run_setup()
