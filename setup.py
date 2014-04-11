from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='lalf',
    version='3.0a0',
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
