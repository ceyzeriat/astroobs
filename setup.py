#!/usr/bin/env python
from sys import argv, exit
import os

if "upl" in argv[1:]:
    os.system("python setup.py register -r pypi")
    os.system("python setup.py sdist upload -r pypi")
    exit()

m = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "astroobs", "_version.py")).read()
version = re.findall(r"__version__ *= *\"(.*?)\"", m)[0]


from distutils.core import setup
setup(
    name = 'astroobs',
    packages = ['astroobs'],
    version = version,
    description = 'Provides astronomy ephemeris to plan telescope observations',
    long_description = open("README.rst").read() + "\n\n"
                    + "Changelog\n"
                    + "---------\n\n"
                    + open("HISTORY.rst").read(),
    license = "GNU General Public License v3 or later (GPLv3+)",
    author = 'Guillaume Schworer',
    author_email = 'guillaume.schworer@obspm.fr',
    url = 'https://github.com/ceyzeriat/astroobs/',
    download_url = 'https://github.com/ceyzeriat/astroobs/tree/master/dist',
    keywords = ['astronomy', 'ephemeris', 'pyephem', 'iobserve', 'observatory', 'telescope', 'observer', 'target', 'airmass'],
    classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Documentation :: Sphinx',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Scientific/Engineering :: Astronomy'],
#    install_requires=[],
    package_data={'': ['obsData.txt']},
    include_package_data = True
)

# http://peterdowns.com/posts/first-time-with-pypi.html
