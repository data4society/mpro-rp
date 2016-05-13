import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'sqlalchemy',
    'psycopg2',
    'alembic',
    'requests',
    'tensorflow'
    ]

setup(name='mpro-rp',
      version='0.0.1',
      description='mpro regular processes',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requires,
      )
