#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lalf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()

with open("lalf/__version__.py") as f:
    exec(f.read())
    
setup(
    name='lalf',
    version=__version__,
    description='Forumactif to phpbb converter',
    long_description=long_description,
    author='Roromis',
    author_email='lalf@openmailbox.org',
    url='https://github.com/Roromis/Lalf-Forumactif',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: French',        
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    license="GNU/GPL v3",
    
    packages=['lalf'],
    install_requires=[
        'pyquery',
        'requests',
        'Pillow'
    ],
    entry_points={
        'console_scripts': [
            'lalf = lalf:main',
        ],
    },
    data_files=[('share/doc/lalf', [
        'config.example.cfg',
        'LICENSE',
        'README.rst',
        'TODO.rst'
    ])]
)
