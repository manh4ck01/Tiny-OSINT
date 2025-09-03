from setuptools import setup, find_packages

setup(
    name="tiny-osint",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "tiny-osint = osint.cli:main",
        ],
    },
)
