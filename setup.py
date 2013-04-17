"""
pchip16 setup routine
"""
from setuptools import setup

setup(name='pchip16',
      version='0.1',
      description='Python chip16 virtual machine',
      url='http://github.com/brookst/pchip16',
      author='Tim Brooks',
      author_email='brooks@skoorb.net',
      packages=['pchip16'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
)
