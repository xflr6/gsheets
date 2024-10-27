import pathlib
from setuptools import setup, find_packages

setup(
    name='gsheets',
    version='0.6.2.dev0',
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
        'CI': 'https://github.com/xflr6/gsheets/actions',
        'Coverage': 'https://codecov.io/gh/xflr6/gsheets',
    },
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.9',
    install_requires=[
        'google-api-python-client',
        'oauth2client>=1.5.0',
    ],
    extras_require={
        'dev': ['tox>=3', 'flake8', 'pep8-naming', 'wheel', 'twine'],
        'test': ['mock>=4', 'pytest>=7', 'pytest-mock>=3', 'pytest-cov'],
        'docs': ['sphinx>=5', 'sphinx-rtd-theme'],
    },
    long_description=pathlib.Path('README.rst').read_text(encoding='utf-8'),
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
