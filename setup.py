# -*- coding: utf-8 -*-
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


dependencies = [
    'requests',
]


test_dependencies = [
    'pytest',
    'hypothesis',
    'pytest-cov'
]


extras = {
    'test': test_dependencies,
}


setup(name='pyserval',
      version='0.1.2',
      description='Python client for serval-dns REST interface',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      url='https://github.com/umr-ds/pyserval',
      author=u'Jonas Höchst & Markus Sommer',
      author_email='msommer@informatik.uni-marburg.de',
      license='MIT',
      packages=['pyserval'],
      package_dir={'': 'src'},
      install_requires=dependencies,
      tests_require=test_dependencies,
      extras_require=extras,
      include_package_data=True,
      zip_safe=True)
