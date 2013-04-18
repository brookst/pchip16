"""
pchip16 setup routine
"""
#pylint: disable=I0011,W0611

from setuptools import setup
# Prevent issue with setup.py test
try:
    import multiprocessing
except ImportError:
    pass

setup(name='pchip16',
      version='0.1',
      description='Python chip16 virtual machine',
      long_description=open('README.rst').read(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Education',
      ],
      url='http://github.com/brookst/pchip16',
      author='Tim Brooks',
      author_email='brooks@skoorb.net',
      packages=['pchip16'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
)
