#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

with open("requirements.txt", "r") as file:
    requirements = file.read().split('\n')

setup(
    name='wichteln',
    version='1.0',
    description='A simple CLI tool to generate and send secret santa assignments.',
    author='Axel Brunnbauer',
    author_email='axel.brunnbauer@gmx.at',
    url='https://github.com/axelbr/secret-santa',
    packages=find_packages(),
    entry_points='''
      [console_scripts]
      wichteln=wichteln.__main__:main
    ''',
    install_requires=requirements,
)
