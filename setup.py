from setuptools import setup, find_packages

setup(
    name="wot-servient",
    version="0.0.1",
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'Flask>=1.1.1',
        'redis>=3.1.0',
        'PyJWT==1.7.1',
        'aiocoap[all]==0.4b1',
        'Click==7.0',
        'requests>=2.21.0',
        'pyHS100>=0.3.5',
        ],
    author="Dan Harris",
    description="Common libraries to be used by microservices in the WoT Servient",
    dependency_links=[
        "git+git://github.com/chrysn/aiocoap.git#egg=aiocoap",
    ],
)
