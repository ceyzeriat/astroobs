# -*- coding: utf-8 -*-
# Written by Guillaume Schworer, 2015
"""
Provides astronomy ephemeris to plan telescope observations

.. note::
  * All altitudes, azimuth, hour angle are in degrees
  * ``horizon`` attribute of :class:`Observatory` or :class:`Observation` is in radian
  * All times are in UT, except for ``Observatory.localnight``

.. warning::
  * it can occur that the Sun, the Moon or a target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``

Real-life example use:
>>> 



"""
__all__ = ['ObservatoryList', 'Observatory', 'Target', 'Moon', 'TargetSIMBAD', 'Observation', 'version']

import obs # left for backward v <= 1.3.7 compatibility

from ObservatoryList import ObservatoryList
from Observatory import Observatory
from Target import Target
from Moon import Moon
from TargetSIMBAD import TargetSIMBAD
from Observation import Observation

from version import __version__, __major__, __minor__
