from setuptools import setup

setup(name='pytisean',
      version='0.1.1',
      description='Python wrapper for the TISEAN package',
      author='Troels Bogeholm Mikkelsen',
      author_email='bogeholm@nbi.ku.dk',
      license='MIT',
      url='https://github.com/bogeholm/pytisean',
      install_requires=[
          'numpy',
          'matplotlib',
          ],
      packages=['pytisean'],
      zip_safe=False)
