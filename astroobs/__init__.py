#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  
#  ASTROOBS - Astronomical Observation
#  Copyright (C) 2015-2016  Guillaume Schworer
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  
#  For any information, bug report, idea, donation, hug, beer, please contact
#    guillaume.schworer@obspm.fr
#
###############################################################################

from time import gmtime as _gmtime

_disclaimer = """ASTROOBS  Copyright (C) 2015-%s  Guillaume Schworer
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.""" % _gmtime()[0]

print(_disclaimer)


"""
Provides astronomy ephemeris to plan telescope observations

.. note::
  * All altitudes, azimuth, hour angle are in degrees
  * However, ``horizon`` attribute of :class:`Observatory` or :class:`Observation` is in radian
  * All times are in UT, except for ``Observatory.localnight`` - obviously

.. warning::
  * it can occur that the Sun, the Moon or a target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``

Real-life example use:
>>> import astroobs as obs
>>> o=obs.Observation('vlt', local_date=(2015, 1, 1), moonAvoidRadius=15, horizon_obs = 40)
>>> o.add_target('aldebaran')
>>> o.add_target('canopus')
>>> o.plot()

"""
__all__ = ['ObservatoryList', 'Observatory', 'Target', 'Moon', 'TargetSIMBAD', 'Observation', '_version']

from . import obs # left for backward v <= 1.3.7 compatibility

from .ObservatoryList import ObservatoryList, show_all_obs
from .Observatory import Observatory
from .Target import Target
from .Moon import Moon
from .TargetSIMBAD import TargetSIMBAD
from .Observation import Observation

from ._version import __version__, __major__, __minor__, __micro__
