#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
#
# The stlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

from setuptools import setup

setup(
    name='stlib-plugins',
    version='0.0.0',
    description='Official plugins for stlib',
    author='Lara Maia',
    author_email='dev@lara.click',
    url='https://github.com/ShyPixie/stlib-plugins',
    license='GPL',
    packages=['stlib_plugins'],
    package_dir={'stlib_plugins': 'src'},
    requires=['aiohttp'],
    python_requires='>=3.6',
    setup_requires=['setuptools'],
    install_requires=['stlib>=0.6'],
    zip_safe=True,
    entry_points={'stlib_plugins': ['steamtrades = stlib_plugins.steamtrades']},
)
