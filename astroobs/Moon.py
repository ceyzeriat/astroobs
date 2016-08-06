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



from . import _core
from . import _astroobsexception as _exc

from .Target import Target

class Moon(Target):
    """
    Initialises the Moon. Optionaly, processes the Moon for the observatory and date given (refer to :func:`Moon.process`).

    Args:
      * obs (:class:`Observatory`) [optional]: the observatory for which to process the Moon

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      N/A
    """
    def __init__(self, obs=None, input_epoch='2000', **kwargs):
        self._raiseError = bool(kwargs.get('raiseError', False))
        self.name = 'Moon'
        self.input_epoch = str(int(input_epoch))
        if obs is not None: self.process(obs=obs, **kwargs)

    def _info(self):
        if not hasattr(self,'phase'):
            if _exc.raiseIt(_exc.NonTarget, self._raiseError): return
        return "Moon - phase: %2.1f%%" % (self.phase.mean())
    @property
    def ra(self):
        """
        The right ascension of the Moon, displayed as tuple of np.array (hh, mm, ss)
        """
        return self._ra.hms
    @ra.setter
    def ra(self, value):
        if _exc.raiseIt(_exc.ReadOnly, self._raiseError, 'ra'): return

    @property
    def dec(self):
        """
        The declination of the Moon, displayed as tuple of np.array (+/-dd, mm, ss)
        """
        return self._dec.dms
    @dec.setter
    def dec(self, value):
        if _exc.raiseIt(_exc.ReadOnly, self._raiseError, 'dec'): return

    @property
    def raStr(self):
        """
        A pretty printable version of the mean of the right ascension of the moon
        """
        hms = self._ra.hms
        return "%ih%im%2.1fs" % (hms[0].mean(), hms[1].mean(), hms[2].mean())
    @raStr.setter
    def raStr(self, value):
        if _exc.raiseIt(_exc.ReadOnly, self._raiseError, 'raStr'): return
    @property
    def decStr(self):
        """
        A pretty printable version of the mean of the declination of the moon
        """
        dms = self._dec.dms
        return "%s%i°%i'%2.1f\"" % ((dms[0].mean()>0)*'+', dms[0].mean(), dms[1].mean(), dms[2].mean())
    @decStr.setter
    def decStr(self, value):
        if _exc.raiseIt(_exc.ReadOnly, self._raiseError, 'decStr'): return

    def plot(self, obs, y='alt', **kwargs):
        """
        Plots the y-parameter vs time diagram for the moon at the given observatory and date

        Args:
          * obs (:class:`Observatory`): the observatory for which to plot the moon

        Kwargs:
          * See :class:`Moon`
          * See :func:`Observatory.plot`
          * See :func:`Target.plot`
        
        Raises:
          N/A
        """
        kwargs['polar'] = False
        kwargs['color'] = kwargs.get('color', '#777777')
        return self._plot(obs=obs, y=y, **kwargs)

    def polar(self, obs, **kwargs):
        """
        Plots the y-parameter vs time diagram for the moon at the given observatory and date

        Args:
          * obs (:class:`Observatory`): the observatory for which to plot the moon

        Kwargs:
          * See :class:`Moon`
          * See :func:`Observatory.plot`
          * See :func:`Target.plot`
        
        Raises:
          N/A
        """
        kwargs['polar'] = True
        kwargs['color'] = kwargs.get('color', '#777777')
        return self._plot(obs=obs, **kwargs)

    def process(self, obs, **kwargs):
        """
        Processes the moon for the given observatory and date.

        Args:
          * obs (:class:`Observatory`): the observatory for which to process the moon

        Kwargs:
          See :class:`Moon`

        Raises:
          N/A

        Creates vector attributes:
          * ``airmass``: the airmass of the moon
          * ``ha``: the hour angle of the moon (degrees)
          * ``alt``: the altitude of the moon (degrees - horizon is 0)
          * ``az``: the azimuth of the moon (degrees)
          * ``ra``: the right ascension of the moon, see :func:`Moon.ra`
          * ``dec``: the declination of the moon, see :func:`Moon.dec`

        .. note::
          * All previous attributes are vectors related to the time vector of the observatory used for processing: ``obs.dates``

        Other attributes:
          * ``rise_time``, ``rise_az``: the time (ephem.Date) and the azimuth (degree) of the rise of the moon
          * ``set_time``, ``set_az``: the time (ephem.Date) and the azimuth (degree) of the setting of the moon
          * ``transit_time``, ``transit_az``: the time (ephem.Date) and the azimuth (degree) of the transit of the moon
        
        .. warning::
          * it can occur that the moon does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``, i.e. ``set_time``, ``set_az``, ``rise_time``, ``rise_az``. In that case, an additional parameter is added to the Moon object: ``Moon.alwaysUp`` which is ``True`` if the Moon never sets and ``False`` if it never rises above the horizon.
        """
        save_date = obs.date # saves the date
        obs.date = _core.E.Date(obs.dates[0])
        self.ha = []
        self.airmass = []
        self.phase = []
        self.alt = []
        self.az = []
        self._ra = []
        self._dec = []
        target = _core.E.Moon()
        self._set_RiseSetTransit(target=target, obs=obs, **kwargs)
        for t in range(len(obs.dates)):
            obs.date = obs.dates[t] # forces obs date for target calculations
            target.compute(obs) # target calculation
            self.phase.append(target.phase)
            self.airmass.append(_core.rad_to_airmass(target.alt))
            self.alt.append(target.alt)
            self.az.append(target.az)
            self._ra.append(target.a_ra)
            self._dec.append(target.a_dec)
            self.ha.append(obs.lst[t] - target.a_ra)
        obs.date = save_date # sets obs date back
        self.alt = _core.np.rad2deg(self.alt)
        self.az = _core.np.rad2deg(self.az)
        self.ha = _core.np.rad2deg(self.ha)
        self._ra = _core.np.rad2deg(_core.Angle(self._ra, 'rad'))
        self._dec = _core.np.rad2deg(_core.Angle(self._dec, 'rad'))
        self.airmass = _core.np.asarray(self.airmass)
        self.phase = _core.np.asarray(self.phase)
