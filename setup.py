# setup.py

from setuptools import setup, find_packages

setup(
    name='gsheets',
    version='0.3.1.dev0',
    author='Sebastian Bank',
    author_email='sebastian.bank@uni-leipzig.de',
    description='Pythonic wrapper for the Google Sheets API',
    keywords='spreadhseets google api v4 wrapper csv pandas',
    license='MIT',
    url='https://github.com/xflr6/gsheets',
    packages=find_packages(),
    install_requires=['google-api-python-client'],
    platforms='any',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
