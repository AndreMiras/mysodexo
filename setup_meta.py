"""
Creates a distribution alias that just installs mysodexo.
"""
from setuptools import setup

from setup import setup_params

setup_params.update({"install_requires": ["mysodexo"], "name": "sodexo"})


setup(**setup_params)
