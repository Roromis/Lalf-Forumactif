from distutils.core import setup

setup(
    name='lalf',
    version='3.0a',
    description='Forumactif to phpbb converter',
    author='Roromis',
#    author_email='',
    url='https://github.com/Roromis/Lalf-Forumactif',
    download_url='https://github.com/Roromis/Lalf-Forumactif/archive/master.zip',
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
    requires=[
        'pyquery',
        'requests',
        'pypng'
    ],
    scripts=['export.py'],
    data_files=[('', [
        'config.example.cfg',
        'README.md',
        'TODO.md'
    ])]
)
