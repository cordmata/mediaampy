from codecs import open
import re
from setuptools import setup, find_packages

version = ''
version_re = r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]'

with open('mediaamp/__init__.py', 'r') as fd:
    version = re.search(version_re, fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='mediaampy',
    version=version,
    description='HTTP Client for the MediaAmp/MPX API',
    long_description=readme,
    author='Matt Cordial',
    url='https://github.com/cordmata/mediaampy',
    packages=find_packages(),
    install_requires=['requests', 'blinker', 'pytz'],
    license='Apache 2.0',
    keywords=('MediaAmp', 'thePlatform'),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
    ),
)
