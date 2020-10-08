from setuptools import setup, find_namespace_packages

setup(
    name="wot-directory",
    version="0.0.1",
    package_dir={"":"src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        'Flask>=1.1.2',
        'tinydb>=4.1.1',
        'requests>=2.24.0',
        'PyYAML>=5.3.1',
        ],
    author="Dan Harris",
    description="API to collate thing descriptions elsewhere on network",
)
