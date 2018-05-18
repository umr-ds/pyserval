# -*- coding: utf-8 -*-
"""Based on the pypa sample-project

See: https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

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

setup(
    name='pyserval',
    version='0.2',
    description='Python client for serval-dna REST interface',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/umr-ds/pyserval',
    author=u'Jonas Höchst & Markus Sommer',
    author_email='msommer@informatik.uni-marburg.de',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='serval dtn',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=dependencies,
    extras_require=extras,
    zip_safe=True,
    project_urls={
        'Bug Reports': 'https://github.com/umr-ds/pyserval/issues',
        'Source': 'https://github.com/umr-ds/pyserval',
    }
)
