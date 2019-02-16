from setuptools import setup, find_packages

setup(
    name="WoT Network",
    version="0.1",
    package_dir={'':'src'},
    packages=find_packages('src', exclude=['*.tests']),
    install_requires=['Flask>=1.0.2', 'requests>=2.21.0', 'redis>=3.1.0', 'pyHS100>=0.3.4'],
    author="Dan Harris",
    description="Set of services used to build a network based on W3 specification",
    entry_points={
        'console_scripts': [
            'wot-td = scripts.main:start_thing_directory',
            'wot-proxy = scripts.main:start_proxy',
            'wot-binding = scripts.main:start_binding'
        ]
    }
)
