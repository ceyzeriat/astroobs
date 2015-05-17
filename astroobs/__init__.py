# -*- coding: utf-8 -*-
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
__all__ = ['obs']

import obs
