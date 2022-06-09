from setuptools import setup, find_packages

__version__ = '0.2'

# This is intentionally an almost direct copy of requirements.txt (except for pyclan)
install_requires = [
      'Distance==0.1.3',
      'mysql-connector==2.2.9',
      'numpy==1.19.2',
      'pandas==1.1.2',
      'python-dateutil==2.8.1',
      'pytz==2020.1',
      'six==1.15.0'
]

setup(name='pyclan',
      version=__version__,
      description='CLAN file library',
      author='Andrei Amatuni',
      author_email='andrei.amatuni@gmail.com',
      license="MIT",
      url='https://github.com/SeedlingsBabylab/pyclan',
      packages=find_packages(),
      install_requires=install_requires
)
