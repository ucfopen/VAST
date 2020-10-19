#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0',
    'beautifulsoup4==4.5.3',
    'bs4==0.0.1',
    'canvasapi',
    'langcodes==1.4.1',
    'requests',
    'six',
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Techrangers",
    author_email='techrangers@ucf.edu',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="VAST is a Python script that searches an Instructure Canvas course for media and returns results in a CSV file.",
    entry_points={
        'console_scripts': [
            'vast=vast.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='vast',
    name='vast',
    packages=find_packages(include=['vast', 'vast.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ucfopen/vast',
    version='1.0.0',
    zip_safe=False,
)
