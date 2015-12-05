from setuptools import setup

setup(name='nastran_pch_reader',
      version='1.0.0',
      description='NASTRAN punch file parser',
      url='https://github.com/anick107/nastran_pch_reader',
      author='Nikolay Asmolovskiy',
      classifiers=[
            'Programming Language :: Python :: 3',
            'Intended Audience :: Structural Engineers',
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
            'Topic :: FEM',
            'Topic :: Parsers',
            'Topic :: Text Processing :: Punch'
      ],
      long_description=__doc__,
      author_email='nick.asmolovsky@gmail.com',
      license='BSD',
      packages=['nastran_pch_reader'],
      zip_safe=False)
