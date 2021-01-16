from setuptools import setup, find_namespace_packages

setup(
    name="wot-adapter",
    version="0.0.1",
    package_dir={"":"src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        'Flask>=1.1.1',
        'Flask-Cors>=3.0.9',
        'pyHS100>=0.3.5',
        'PyYAML>=5.3.1',
        'requests>=2.25.1',
        'paho-mqtt>=1.5.1',
        ],
    author="Dan Harris",
    description="Common libraries to be used by microservices in the WoT Servient",
    dependency_links=[
        "git+git://github.com/chrysn/aiocoap.git#egg=aiocoap",
    ],
)
