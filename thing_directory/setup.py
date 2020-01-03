from setuptools import setup, find_namespace_packages

setup(
    name="wot-thing-directory",
    version="0.0.1",
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=[
        'Flask>=1.1.1',
        'requests>=2.21.0',
        'Click==7.0',
        'aiocoap[all]==0.4b1',
        ],
    author="Dan Harris",
    description="Thing Directory microservice in the WoT Servient",
    dependency_links=[
        "git+git://github.com/chrysn/aiocoap.git#egg=aiocoap",
    ],
)
