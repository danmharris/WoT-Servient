from setuptools import setup, find_namespace_packages

setup(
    name="wot-common",
    version="0.0.1",
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=[
        'Flask>=1.1.1',
        'redis>=3.1.0',
        'PyJWT==1.7.1',
        'aiocoap[all]==0.4b1',
        ],
    author="Dan Harris",
    description="Common libraries to be used by microservices in the WoT Servient",
    dependency_links=[
        "git+git://github.com/chrysn/aiocoap.git#egg=aiocoap",
    ],
)
