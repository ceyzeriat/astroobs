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

from .Observatory import Observatory
from .Target import Target
from .TargetSIMBAD import TargetSIMBAD

class Observation(Observatory):
    """
    Assembles together an :class:`Observatory` (including itself the :class:`Moon` target), and a list of :class:`Target`.

    For use and docs refer to:
      * :func:`add_target` to add a target to the list
      * :func:`rem_target` to remove one
      * :func:`change_obs` to change the observatory
      * :func:`change_date` to change the date of observation

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``
      * fig: TBD

    Raises:
      See :class:`Observatory`

    .. warning::
      * it can occur that the Sun, the Moon or a target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``

    >>> import astroobs.obs as obs
    >>> o = obs.Observation('ohp', local_date=(2015,3,31,23,59,59))
    >>> o
    Observation at Observatoire de Haute Provence on 2015/6/21-22. 0 targets.
        Moon phase: 89.2%
    >>> o.moon
    Moon - phase: 89.2%
    >>> print o.sunset, '...', o.sunrise, '...', o.len_night
    2015/3/31 18:08:40 ... 2015/4/1 05:13:09 ... 11.0746939826
    >>> import ephem as E
    >>> print(E.Date(o.sunsetastro+o.localTimeOffest), '...', E.Date(
            o.sunriseastro+o.localTimeOffest), '...', o.len_nightastro)
    2015/3/31 21:43:28 ... 2015/4/1 05:38:26 ... 7.91603336949
    >>> o.add_target('vega')
    >>> o.add_target('mystar', dec=19.1824, ra=213.9153)
    >>> o.targets
    [Target: 'vega', 18h36m56.3s +38°35'8.1", O,
     Target: 'mystar', 14h15m39.7s +19°16'43.8", O]
    >>> print("%s mags: 'K': %2.2f, 'R': %2.2f"%(o.targets[0].name,
            o.targets[0].flux['K'], o.targets[0].flux['R']))
    vega mags: 'K': 0.13, 'R': 0.07
    """
    def _info(self):
        if not hasattr(self,'localnight') or not hasattr(self,'name') or not hasattr(self,'moon'):
            if _exc.raiseIt(_exc.NonObservatory, self._raiseError, obs): return
        nextday = _core.E.Date(_core.E.Date(self.localnight)+1).datetime()
        nextdaystr = [str(nextday.day)]
        if nextday.month!=self.localnight.month: nextdaystr = [str(nextday.month)] + nextdaystr
        if nextday.year!=self.localnight.year: nextdaystr = [str(nextday.year)] + nextdaystr
        return "Observation at %s on %i/%i/%i-%s. %i targets. Moon phase: %2.1f%%" % (self.name, self.localnight.year, self.localnight.month, self.localnight.day, "/".join(nextdaystr), len(self.targets), self.moon.phase.mean())
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    @property
    def targets(self):
        """
        Shows the list of targets recorded into the Observation
        """
        if not hasattr(self, '_targets'): self._targets = []
        return self._targets
    @targets.setter
    def targets(self, value, **kwargs):
        if not isinstance(value, (list, tuple)): # single element
            # check if the target is not valid
            if not isinstance(value, Target):
                if _exc.raiseIt(_exc.NonTarget, self._raiseError, value): return
            self._targets = [value]
            self._targets[0]._ticked = True
        else: # list of elements
            # check if any of the target is not valid
            for item in value:
                if not isinstance(item, Target):
                    if _exc.raiseIt(_exc.NonTarget, self._raiseError, item): return
            self._targets = value
            for item in self._targets:
                item._ticked = True
                item.process(obs=self, **kwargs)

    @property
    def ticked(self):
        """
        Shows whether the target was select for observation
        """
        if not hasattr(self, '_targets'): return []
        return [item._ticked for item in self._targets]
    @ticked.setter
    def ticked(self, value):
        if _exc.raiseIt(_exc.ReadOnly, self._raiseError, "ticked"): return

    def tick(self, tgt, forceTo=None, **kwargs):
        """
        Changes the ticked property of a target (whether it is selected for observation)

        Args:
          * tgt (int): the index of the target in the ``Observation.targets`` list
          * forceTo (bool) [optional]: if ``True``, selects the target for observation, if ``False``, unselects it, if ``None``, the value of the selection is inverted
        
        Kwargs:
          See :class:`Observation`

        Raises:
          N/A

        .. note::
          * Automatically reprocesses the target for the given observatory and date if it is selected for observation

        >>> import astroobs.obs as obs
        >>> o = obs.Observation('ohp', local_date=(2015,3,31,23,59,59))
        >>> o.add_target('arcturus')
        >>> o.targets
        [Target: 'arcturus', 14h15m39.7s +19°16'43.8", O]
        >>> o.tick(4)
        >>> o.targets
        [Target: 'arcturus', 14h15m39.7s +19°16'43.8", -]
        """
        if not hasattr(self, '_targets') or not isinstance(tgt, int): return None
        if forceTo is not None:
            self._targets[tgt]._ticked = bool(forceTo)
        else:
            self._targets[tgt]._ticked = not bool(self._targets[tgt]._ticked)
        if self._targets[tgt]._ticked: self._targets[tgt].process(self, **kwargs)
    

    def add_target(self, tgt, ra=None, dec=None, name="", **kwargs):
        """
        Adds a target to the observation list
        
        Args:
          * tgt (see below): the index of the target in the ``Observation.targets`` list
          * ra ('hh:mm:ss.s' or decimal degree) [optional]: the right ascension of the target to add to the observation list. See below
          * dec ('+/-dd:mm:ss.s' or decimal degree) [optional]: the declination of the target to add to the observation list. See below
          * name (string) [optional]: the name of the target to add to the observation list. See below
        
        ``tgt`` arg can be:
          * a :class:`Target` instance: all other parameters are ignored
          * a target name (string): if ``ra`` and ``dec`` are not ``None``, the target is added with the provided coordinates; if ``None``, a SIMBAD search is performed on ``tgt``. ``name`` is ignored
          * a ra-dec string ('hh:mm:ss.s +/-dd:mm:ss.s'): in that case, ``ra`` and ``dec`` will be ignored and ``name`` will be the name of the target

        Kwargs:
          See :class:`Observation`

        Raises:
          * ValueError: if ra-dec formating was not understood

        .. note::
          * Automatically processes the target for the given observatory and date

        >>> import astroobs.obs as obs
        >>> o = obs.Observation('ohp', local_date=(2015,3,31,23,59,59))
        >>> arc = obs.TargetSIMBAD('arcturus')
        >>> o.add_target(arc)
        >>> o.add_target('arcturus')
        >>> o.add_target('arcturusILoveYou', dec=19.1824, ra=213.9153)
        >>> o.add_target('14:15:39.67 +10:10:56.67', name='arcturus')
        >>> o.targets 
        [Target: 'arcturus', 14h15m39.7s +19°16'43.8", O,
         Target: 'arcturus', 14h15m39.7s +19°16'43.8", O,
         Target: 'arcturus', 14h15m39.7s +10°40'43.8", O,
         Target: 'arcturus', 14h15m39.7s +19°16'43.8", O]
        """
        if not hasattr(self, '_targets'): self._targets = []
        if isinstance(tgt, Target): # if we got a target
            self._targets += [tgt]
        elif ra is not None and dec is not None: # if we got some ra and dec coordinates
            self._targets += [Target(ra=ra, dec=dec, name=tgt, **kwargs)]
        elif isinstance(tgt, str): # if we got random shit or string
            try:
                ra, dec = _core.radecFromStr(str(tgt)) # does it look like a coordinates string?
                tt = Target(ra=ra, dec=dec, name=name, **kwargs)
                self._targets += [tt]
            except: # let's try simbad
                tt = TargetSIMBAD(name=tgt, **kwargs)
                if not getattr(tt, '_error', False):
                    self._targets += [tt]
                else:
                    return
        else:
            _exc.raiseIt(_exc.InputNotUnderstood, self._raiseError, tgt)
            return
        self._targets[-1]._ticked = True
        self._targets[-1].process(obs=self, **kwargs)

    def rem_target(self, tgt, **kwargs):
        """
        Removes a target from the observation list

        Args:
          * tgt (int): the index of the target in the ``Observation.targets`` list

        Kwargs:
          See :class:`Observation`

        Raises:
          N/A
        """
        if not hasattr(self, '_targets'): return None
        if isinstance(tgt, int): self._targets.pop(tgt)

    def change_obs(self, obs, long=None, lat=None, elevation=None, timezone=None, temp=None, pressure=None, moonAvoidRadius=None, horizon_obs=None, dataFile=None, recalcAll=False, **kwargs):
        """
        Changes the observatory and optionaly re-processes all target for the new observatory and same date

        Args:
          * recalcAll (bool or None) [optional]: if ``False`` (default): only targets selected for observation are re-processed, if ``True``: all targets are re-processed, if ``None``: no re-process

        Kwargs:
          See :class:`Observation`

        .. note::
          * Refer to :func:`ObservatoryList.add` for details on other input parameters
        """
        targets = self._targets
        Observation.__init__(self, obs=obs, long=long, lat=lat, elevation=elevation, timezone=timezone, temp=temp, pressure=pressure, moonAvoidRadius=moonAvoidRadius, local_date=self.localnight, horizon_obs=horizon_obs, dataFile=dataFile, **kwargs)
        self._targets = targets
        if recalcAll is not None: self._process(recalcAll=recalcAll, **kwargs)


    def _process(self, recalcAll=False, **kwargs):
        """
        Processes all target for the given observatory and date
        Args:
          * recalcAll (bool or None) [optional]: if ``False`` (default): only targets selected for observation are re-processed, if ``True``: all targets are re-processed, if ``None``: no re-process
        """
        for item in self.targets:
            if item._ticked or recalcAll: item.process(self, **kwargs)
        

    def change_date(self, ut_date=None, local_date=None, recalcAll=False, **kwargs):
        """
        Changes the date of the observation and optionaly re-processes targets for the same observatory and new date

        Args:
          * ut_date: Refer to :func:`Observatory.upd_date`
          * local_date: Refer to :func:`Observatory.upd_date`
          * recalcAll (bool or None) [optional]: if ``False`` (default): only targets selected for observation are re-processed, if ``True``: all targets are re-processed, if ``None``: no re-process

        Kwargs:
          See :class:`Observation`

        Raises:
          * KeyError: if the twilight keyword is unknown
          * Exception: if the observatory object has no date

        """
        self.upd_date(ut_date=ut_date, local_date=local_date, **kwargs)
        if recalcAll is not None: self._process(recalcAll=recalcAll, **kwargs)

    def plot(self, y='alt', **kwargs):
        """
        Plots the y-parameter vs time diagram for the target at the given observatory and date

        Kwargs:
          * See :class:`Observation`
          * moon (bool): if ``True``, adds the moon to the graph, default is ``True``
          * autocolor (bool): if ``True``, sets curves-colors automatically, default is ``True``
          * time (str): the type of the x-axis time, ``ut`` for UT, ``loc`` for local time and ``lst`` [0-24] for local sidereal time, default is ``ut`` (not with polar mode)
          * dt (float - hour): the spacing of x-axis labels, default is 1 hour (not with polar mode)
          * t0 (float - DJD or [0-24]): the date of the first tick-label of x-axis, default is sunsetastro. The time type must correspond to ``time`` parameter (not with polar mode)
          * xlim ([xmin, xmax]): bounds for x-axis, default is full night span (not with polar mode)
          * retxdisp (bool): if ``True``, bounds of x-axis displayed values are returned (``xdisp`` key)
          * ylim ([ymin, ymax]): bounds for y-axis, default is [horizon_obs-10, 90] (not with polar mode)
          * xlabel (str): label for x-axis, default 'Time (UT)'
          * ylabel (str): label for y-axis, default 'Elevation (°)'
          * title (str): title of the diagram, default is observatory name or coordinates
          * ymin_margin (float): margin between xmin of graph and horizon_obs. Low priority vs ylim, default is 10 (not with polar mode)
          * retfignum (bool): if ``True``, the figure number will be returned, default is ``False``
          * fignum (int): figure number on which to plot, default is ``False``
          * retaxnum (bool): if ``True``, the ax index as in ``figure.axes[n]`` will be returned, default is ``False``
          * axnum (int): axes index on which to plot, default is ``None`` (create new ax)
          * retfig (bool): if ``True``, the figure object will be returned, default is ``False``
          * fig (figure): figure object on which to plot, default is ``None`` (use fignum)
          * retax (bool): if ``True``, the ax will be returned, default is ``False``
          * ax (axes): ax on which to plot, default is ``None``
          * now (bool): if ``True`` and within range, a vertical line as indication of "now" will be shown, default is True
          * retnow (bool): returns the line object (``nowline`` key) corresponding to the 'now-line', default is ``False``
          * legend (bool): whether to add a legend or not, default is ``True``
          * loc: location of the legend, default is 8 (top right), refer to plt.legend
          * ncol: number of columns in the legend, default is 3, refer to plt.legend
          * columnspacing: spacing between columns in the legend, refer to plt.legend
          * lfs: legend font size, default is 11
          * textlbl (bool): if ``True``, a text label with target name or coordinates will be added near transit, default is ``False``
          * polar (bool): if ``True``, plots the sky view, otherwise plots target attribute versus time

        Raises:
          N/A
        """
        if kwargs.get('polar', False):
            if self.polar(**kwargs) != {}:
                return retkwargs
            return
        saveretax = kwargs.get('retax', False)
        kwargs['retax'] = True
        kwargs['polar'] = False
        retkwargs = self._plot(**kwargs)
        kwargs['ax'] = retkwargs['ax']
        kwargs['simpleplt'] = True
        colindex = 0
        for item in self.targets:
            if item._ticked and item.name.lower()!="moon":
                if kwargs.get('autocolor', True): kwargs['color'] = _core.many_color[colindex%len(_core.many_color)]
                item.plot(self, y=y, **kwargs)
                colindex += 1
        if 'color' in kwargs.keys(): kwargs.pop('color')
        if kwargs.get('moon', True): self.moon.plot(self, y=y, **kwargs)
        if not saveretax: retkwargs.pop('ax')
        if retkwargs != {}: return retkwargs

    def polar(self, **kwargs):
        """
        Plots the sky-view diagram for the target at the given observatory and date

        Kwargs:
          * See :class:`Observation`
          * See :func:`Observatory.plot`

        Raises:
          N/A
        """
        saveretax = kwargs.get('retax', False)
        kwargs['retax'] = True
        kwargs['polar'] = True
        retkwargs = self._plot(**kwargs)
        kwargs['ax'] = retkwargs['ax']
        kwargs['simpleplt'] = True
        colindex = 0
        nowArg = self.nowArg # take now time
        if kwargs.get('now', False) and nowArg is not None: kwargs['gemmenow'] = nowArg # time parameter to pass to each item to plot
        thenowline = []
        for item in self.targets:
            if item._ticked and item.name.lower()!="moon":
                if kwargs.get('autocolor', True): kwargs['color'] = _core.many_color[colindex%len(_core.many_color)]
                ret = item.polar(self, **kwargs)
                if isinstance(ret, dict): thenowline.append(ret.get('nowline', None))
                colindex += 1
        if 'color' in kwargs.keys(): kwargs.pop('color')
        if kwargs.get('moon', True):
            ret = self.moon.polar(self, **kwargs)
            if isinstance(ret, dict): thenowline.append(ret.get('nowline', None))
        if not saveretax: retkwargs.pop('ax')
        if nowArg is not None and kwargs.get('retnow', False): retkwargs['nowline'] = [item for item in thenowline if item is not None]
        if retkwargs!={}: return retkwargs
