from setuptools import setup

setup(name='nastran_pch_reader',
      version='1.0.2',
      description='NASTRAN punch file parser',
      url='https://github.com/anick107/nastran_pch_reader',
      author='Nikolay Asmolovskiy',
      classifiers=[
            'Programming Language :: Python :: 3',
            'Intended Audience :: Other Audience',
            'License :: OSI Approved :: BSD License',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
            'Topic :: Text Processing'
      ],
      py_modules=['nastran_pch_reader'],
      long_description=__doc__,
      author_email='nick.asmolovsky@gmail.com',
      license='BSD',
      zip_safe=False)
