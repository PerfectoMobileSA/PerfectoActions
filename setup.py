#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 16:56:12 2020

@author: genesisthomas
"""

import sys

from setuptools import find_packages, setup

OPTIONS = {}
mainscript = 'perfecto/perfectoactions.py'
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
     name='perfectoactions',
    #  version='1.0.68', #testpypi
      version='2.0.18',
     author="Genesis Thomas",
     author_email="gthomas@perforce.com",
     description="A Perfecto device actions execution + reporter package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     license='GPLv3',
     keywords = ['Perfecto', 'appium', 'selenium', 'testing', 'api', 'automation'],
     url="https://github.com/PerfectoMobileSA/Device_actions_reporter",
     install_requires=[
             'requests','configparser','termcolor', 'pandas','matplotlib', 'colorama', 'openpyxl', 'xlrd', 'jinja2', 'tzlocal', 'ipython', 'xlwt'
      ],
     packages=find_packages(),
     include_package_data=True,
     classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
         'Operating System :: OS Independent'
     ],
     entry_points={"console_scripts": ["perfectoactions=perfecto.perfectoactions:main"]}
 )
