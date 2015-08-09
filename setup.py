from setuptools import setup, find_packages
from os import path
from iio import __version__
import io


here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='python-iio',
    version=__version__,
    description='Module to access Linux IIO devices',
    long_description=long_description,
    url='https://github.com/zathras777/python-iio',
    author='david reid',
    author_email='zathrasorama@gmail.com',
    license='Unlicense',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='i2c iio linux',
    packages=find_packages(exclude=['tests']),
    test_suite='tests',
    install_requires=[
        'Quaternion'
    ],
    entry_points={
        'console_scripts': ['python-iio=iio.command_line:main']
    },
)
