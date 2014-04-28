#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        'pypng'
    ],
    scripts=['lalf.py'],
    data_files=[('share/doc/lalf', [
        'config.example.cfg',
        'README.rst',
        'TODO.rst'
    ])]
)
