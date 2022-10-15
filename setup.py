#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2022
#
# The stlib-plugins is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib-plugins is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

from setuptools import setup

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Games/Entertainment',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Typing :: Typed',
]

try:
    with open('README.md') as readme:
        long_description = readme.read()
except FileNotFoundError:
    long_description = ''

setup(
    name='stlib-plugins',
    version='1.1',
    description="Official stlib plugins",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Lara Maia',
    author_email='dev@lara.monster',
    url='https://github.com/ShyPixie/stlib-plugins',
    license='GPLv3',
    classifiers=classifiers,
    keywords='steam-tools steam stlib valve',
    install_requires=[
        'stlib>=1.0',
    ],
    python_requires='>=3.9',
)
