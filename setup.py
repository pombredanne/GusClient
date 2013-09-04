from setuptools import setup, find_packages

setup(
    name='gus_client',
    version='0.2.4',
    author='Shawn Crosby',
    author_email='scrosby@salesforce.com',
    packages=find_packages(),
    license='Keep it real',
    description='Connect to GUS',
    long_description=open('README.txt').read(),
    install_requires=[
        "simple_salesforce >= 0.51",
        "sc_pylibs>=0.1.1",
    ],
)