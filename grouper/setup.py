from setuptools import setup, find_namespace_packages

setup(
    name="wot-grouper",
    version="0.0.1",
    package_dir={"":"src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        'Flask>=1.1.2',
        'tinydb>=4.1.1',
        ],
    author="Dan Harris",
    description="API to consume one/more things and expose them as a single item",
)
