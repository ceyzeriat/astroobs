# -*- coding: utf-8 -*-
# 
# Copyright ASTROOBS (c) 2015-20016 Guillaume SCHWORER
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 
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

from . import obs # left for backward v <= 1.3.7 compatibility

from .ObservatoryList import ObservatoryList
from .Observatory import Observatory
from .Target import Target
from .Moon import Moon
from .TargetSIMBAD import TargetSIMBAD
from .Observation import Observation

from .version import __version__, __major__, __minor__
