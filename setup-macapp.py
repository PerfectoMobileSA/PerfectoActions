#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 16:56:12 2020

@author: genesisthomas
"""

import sys
from setuptools import setup, find_packages
OPTIONS = {}
mainscript = 'perfecto/perfectoactions.py'
with open("README.md", "r") as fh:
    long_description = fh.read()

if sys.platform == 'darwin': 
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        options={'py2app': OPTIONS},
    )
elif sys.platform == 'win32':
    extra_options = dict( 
        setup_requires=['py2exe'], 
        app=[mainscript],
    ) 
else:
    extra_options = dict(
    # Normally unix-like platforms will use "setup.py install" # and install the main script as such 
        scripts=[mainscript],
)
setup(
     name='perfectoactions',
     version='0.0.16',
     author="Genesis Thomas",
     author_email="gthomas@perforce.com",
     description="A Perfecto device actions execution + reporter package",
     long_description=long_description,
     long_description_content_type="text/markdown",
     license='GPLv3',
     keywords = ['Perfecto', 'appium', 'selenium', 'testing', 'api', 'automation'],
     url="https://github.com/PerfectoMobileSA/Device_actions_reporter",
     install_requires=[
            'requests','configparser','termcolor', 'pandas','matplotlib'
      ],
     packages=find_packages(),
     include_package_data=True,
     classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
         'Operating System :: OS Independent'
     ],
     entry_points={"console_scripts": ["perfectoactions=perfecto.perfectoactions:main"]},
     **extra_options
 )
