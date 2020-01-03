from setuptools import setup, find_namespace_packages

setup(
    name="wot-coap-thing",
    version="0.0.1",
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=[
        'aiocoap[all]==0.4b1',
        ],
    author="Dan Harris",
    description="Test CoAP WoT Thing",
    dependency_links=[
        "git+git://github.com/chrysn/aiocoap.git#egg=aiocoap",
    ],
)
