.. astroobs

:Name: astroobs
:Website: https://github.com/ceyzeriat/astroobs
:Author: Guillaume Schworer
:Version: 1.4.4

Check the `astroobs.eu`_ website for a friendly web-interface of that library! (soon)

.. _`astroobs.eu`: http://astroobs.eu/

Astroobs provides astronomy ephemeris (airmass, azimuth, altitude, moon separation, etc) of a night sky target as a function of the date-time and the longitude/latitude of the observer.
A list of international observatories is provided as well as a SIMBAD-querier to easily import targets.
This package is based on pyephem ephemeris calculations. The main difference with this latter package is that astroobs provides a very straight-forward library for the observer to get the critical information in order to plan an observation.
It also provides convenient turn-key tools to convert epochs and plot diagrams.
It is released under the GNU General Public License v3 or later (GPLv3+).

.. code-block:: python

    import astroobs as obs

    o=obs.Observation('vlt', local_date=(2015, 1, 1), moonAvoidRadius=15, horizon_obs = 40)
    o.add_target('aldebaran')
    o.add_target('canopus')
    o.plot()

.. image:: https://raw.githubusercontent.com/ceyzeriat/astroobs/master/img/obs_ex.png
   :align: center

.. code-block:: python

    aldebaran = o.targets[0]
    aldebaran.whenobs(o, (2015,1,1), (2015, 2, 1))

.. image:: https://raw.githubusercontent.com/ceyzeriat/astroobs/master/img/aldebaran_when.png
   :align: center

Documentation
=============

Refer to this page, http://pythonhosted.org/astroobs/astroobs.html


Requirements
============

astroobs requires the following Python packages:

* NumPy: for basic numerical routines
* Astropy: for angle units
* Astroquery: for querying Simbad
* pyephem: for the calculations of ephemeris
* matplotlib: for plotting (optional)
* pytz: for timezones management
* re, os, sys, datetime, time: for basic stuff

astroobs is tested on Linux and Python 2.7 only, but should cross-plateform and python3 friendly without too many issues.

Installation
============

The easiest and fastest way for you to get the package and run is to install astroobs through pip::

  $ pip install astroobs

You can also download astroobs source from GitHub and type::

  $ python setup.py install

Dependencies will not be installed automatically. Refer to the requirements section. If you have an anaconda distribution, you will only need to install astroquery and pyephem.

Contributing
============

Code writing
------------

Code contributions are welcome! Just send a pull request on GitHub and we will discuss it. In the `issue tracker`_ you may find pending tasks.

Bug reporting
-------------

If you think you've found one please refer to the `issue tracker`_ on GitHub.

.. _`issue tracker`: https://github.com/ceyzeriat/astroobs/issues

Additional options
------------------

You can either send me an e-mail or add it to the issues/wishes list on GitHub.

Citing
======

If you use astroobs on your project, please
`drop me a line <mailto:{my first name}.{my family name}@obspm.fr>`, you will get fixes and additional options earlier.

License
=======

astroobs is released under the GNU General Public License v3 or later (GPLv3+). Please refer to the LICENSE file.
