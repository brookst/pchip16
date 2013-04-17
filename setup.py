"""
pchip16 setup routine
"""
#pylint: disable=W0611

from setuptools import setup
try:
    import multiprocessing
except ImportError:
    pass

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
