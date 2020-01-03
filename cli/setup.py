from setuptools import setup, find_namespace_packages

setup(
    name="wot-cli",
    version="0.0.1",
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=[
        'Click==7.0',
        'aiocoap[all]==0.4b1',
        ],
    author="Dan Harris",
    description="CLI to perform utility functions on the WoT Servient",
    dependency_links=[
        "git+git://github.com/chrysn/aiocoap.git#egg=aiocoap",
    ],
    entry_points={
        'console_scripts': [
            'wot-cli = wot.cli.cli:cli',
        ]
    }
)
