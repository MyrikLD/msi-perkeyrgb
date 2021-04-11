#!/usr/bin/env python
from os.path import dirname, join
from setuptools import setup, find_packages
from msi_perkeyrgb_gui.main import __version__

setup(
    name="msi-perkeyrgb-gui",
    version=__version__,
    description="Configuration tool GUI for per-key RGB keyboards on MSI laptops.",
    long_description=open(join(dirname(__file__), "README.md")).read(),
    url="https://github.com/MyrikLD/msi-perkeyrgb-gui",
    author="Sergey Yorsh",
    author_email="myrik260138@gmail.com",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "msi-perkeyrgb-gui=msi_perkeyrgb_gui.main:main",
        ],
    },
    package_data={
        "msi_perkeyrgb_gui": [
            "protocol_data/presets/*.json",
            "images/*.png",
            "configs/*.msic",
            "bindings/*.json",
        ]
    },
    keywords=["msi", "rgb", "keyboard", "per-key"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
