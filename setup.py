# setup.py

import io
from setuptools import setup, find_packages

setup(
    name='gsheets',
    version='0.5.2.dev0',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Pythonic wrapper for the Google Sheets API',
    keywords='spreadhseets google api v4 wrapper csv pandas',
    license='MIT',
    url='https://github.com/xflr6/gsheets',
    project_urls={
        'Documentation': 'https://gsheets.readthedocs.io',
        'Changelog': 'https://gsheets.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/xflr6/gsheets/issues',
    },
    packages=find_packages(),
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=[
        'google-api-python-client<1.8; python_version < "3"',
        'google-api-python-client; python_version >= "3"',
        'oauth2client>=1.5.0',
    ],
    extras_require={
        'dev': ['tox>=3', 'flake8', 'pep8-naming', 'wheel', 'twine'],
        'test': ['mock>=3', 'pytest>=4', 'pytest-mock>=2', 'pytest-cov'],
        'docs': ['sphinx>=1.8', 'sphinx-rtd-theme'],
    },
    long_description=io.open('README.rst', encoding='utf-8').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
