from distutils.core import setup

__version__ = '0.1'

setup(name='pyclan',
      version=__version__,
      description='CLAN file library',
      author='Andrei Amatuni',
      author_email='andrei.amatuni@gmail.com',
      license="MIT",
      url='https://github.com/SeedlingsBabylab/pyclan',
      packages=['distutils', 'distutils.command'],
)