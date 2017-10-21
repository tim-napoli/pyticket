#!/usr/bin/env python3
import sys
import os.path
from setuptools import setup

def readme():
    with open("README.md", "r") as f:
        return f.read()

COMPLETION_PATH = '/etc/bash_completion.d'
if "--user" in sys.argv:
    COMPLETION_PATH = os.path.expanduser("~/.bash_completion.d")

setup(name='pyticket',
      version='0.0.1',
      description='A local command-line ticket manager.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
      ],
      keywords='ticket manager',
      author='Timothée Napoli',
      author_email='tim@tnapoli.fr',
      license='WTFPL',
      url='https://github.com/tim-napoli/pyticket',
      packages=['pyticket', 'pyticket.commands'],
      data_files=[(COMPLETION_PATH, ['extras/completion/pyticket'])],
      install_requires=['vmd'],
      scripts=['bin/pyticket'],
      include_package_data=True
)
