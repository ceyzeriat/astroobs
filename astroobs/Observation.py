# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Guillaume SCHWORER
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

import core as _core
import astroobsexception as _exc

from Observatory import Observatory
from Target import Target
from TargetSIMBAD import TargetSIMBAD

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
    >>> print E.Date(o.sunsetastro+o.localTimeOffest), '...', E.Date(
            o.sunriseastro+o.localTimeOffest), '...', o.len_nightastro
    2015/3/31 21:43:28 ... 2015/4/1 05:38:26 ... 7.91603336949
    >>> o.add_target('vega')
    >>> o.add_target('mystar', dec=19.1824, ra=213.9153)
    >>> o.targets
    [Target: 'vega', 18h36m56.3s +38°35'8.1", O,
     Target: 'mystar', 14h15m39.7s +19°16'43.8", O]
    >>> print "%s mags: 'K': %2.2f, 'R': %2.2f"%(o.targets[0].name,
            o.targets[0].flux['K'], o.targets[0].flux['R'])
    vega mags: 'K': 0.13, 'R': 0.07
    """
    def _info(self):
        if not hasattr(self,'localnight') or not hasattr(self,'name') or not hasattr(self,'moon'):
            if raiseIt(_exc.NonObservatory, self._raiseError, obs): return
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
                if raiseIt(_exc.NonTarget, self._raiseError, value): return
            self._targets = [value]
            self._targets[0]._ticked = True
        else: # list of elements
            # check if any of the target is not valid
            for item in value:
                if not isinstance(item, Target):
                    if raiseIt(_exc.NonTarget, self._raiseError, item): return
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
        if raiseIt(_exc.ReadOnly, self._raiseError, "ticked"): return

    def tick(self, tgt, forceTo=None, **kwargs):
        """
        Changes the ticked property of a target (whether it is selected for observation)

        Args:
          * tgt (int): the index of the target in the ``Observation.targets`` list
          * forceTo (bool) [optional]: if ``True``, selects the target for observation, if ``False``, unselects it, if ``None``, the value of the selection is inverted
        
        Kwargs:
          See class constructor

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
        if self._targets[tgt]._ticked is True: self._targets[tgt].process(self, **kwargs)
    

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
          See class constructor

        Raises:
          * ValueError: if ra-dec formating was not understood

        .. note::
          * Automatically processes the target for the given observatory and date

        >>> import astroobs.obs as obs
        >>> o = obs.Observation('ohp', local_date=(2015,3,31,23,59,59))
        >>> arc = obs.TargetSIMBAD('arcturus')
        >>> o.add_target(arc)
        >>> o.add_target('arcturus')
        >>> o.add_target('arcturus', dec=19.1824, ra=213.9153)
        >>> o.add_target('14:15:39.67 +10:10:56.67', name='arcturus')
        >>> o.targets 
        [Target: 'arcturus', 14h15m39.7s +19°16'43.8", O,
         Target: 'arcturus', 14h15m39.7s +19°16'43.8", O,
         Target: 'arcturus', 14h15m39.7s +10°40'43.8", O,
         Target: 'arcturus', 14h15m39.7s +19°16'43.8", O]
        """
        if not hasattr(self, '_targets'): self._targets = []
        if isinstance(tgt, Target):
            self._targets += [tgt]
        elif ra is not None and dec is not None:
            self._targets += [Target(ra=ra, dec=dec, name=tgt, **kwargs)]
        elif isinstance(tgt, (int, float, str)): # if we have a ra-dec string
            try:
                ra, dec = _core.radecFromStr(str(tgt))
                tt = Target(ra=ra, dec=dec, name=name, **kwargs)
                self._targets += [tt]
            except:
                tt = TargetSIMBAD(name=tgt)
                if getattr(tt, '_error', False) is False:
                    self._targets += [tt]
                else:
                    return
        self._targets[-1]._ticked = True
        self._targets[-1].process(obs=self, **kwargs)

    def rem_target(self, tgt, **kwargs):
        """
        Removes a target from the observation list

        Args:
          * tgt (int): the index of the target in the ``Observation.targets`` list

        Kwargs:
          See class constructor

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
          See class constructor

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
          See class constructor

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
          * See class constructor
          * See :func:`Observatory.plot`
          * moon (bool): if ``True``, adds the moon to the graph, default is ``True``
          * autocolor (bool): if ``True``, sets curves-colors automatically, default is ``True``

        Raises:
          N/A
        """
        saveretax = kwargs.get('retax', False)
        kwargs['retax'] = True
        kwargs['polar'] = False
        retkwargs = self._plot(**kwargs)
        kwargs['ax'] = retkwargs['ax']
        kwargs['simpleplt'] = True
        colindex = 0
        for item in self.targets:
            if item._ticked is True and item.name.lower()!="moon":
                if kwargs.get('autocolor', True): kwargs['color'] = _core.many_color[colindex%len(_core.many_color)]
                item.plot(self, y=y, **kwargs)
                colindex += 1
        if kwargs.has_key('color'): kwargs.pop('color')
        if kwargs.get('moon', True) is True: self.moon.plot(self, y=y, **kwargs)
        if saveretax is False: retkwargs.pop('ax')
        if retkwargs!={}: return retkwargs

    def polar(self, **kwargs):
        """
        Plots the sky-view diagram for the target at the given observatory and date

        Kwargs:
          * See class constructor
          * See :func:`Observatory.plot`
          * moon (bool): if ``True``, adds the moon to the graph, default is ``True``
          * autocolor (bool): if ``True``, sets curves-colors automatically, default is ``True``

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
        if kwargs.get('now') is True and nowArg is not None: kwargs['gemmenow'] = nowArg # time parameter to pass to each item to plot
        thenowline = []
        for item in self.targets:
            if item._ticked is True and item.name.lower()!="moon":
                if kwargs.get('autocolor', True): kwargs['color'] = _core.many_color[colindex%len(_core.many_color)]
                ret = item.polar(self, **kwargs)
                if isinstance(ret, dict) is True: thenowline.append(ret.get('nowline', None))
                colindex += 1
        if kwargs.has_key('color'): kwargs.pop('color')
        if kwargs.get('moon', True) is True:
            ret = self.moon.polar(self, **kwargs)
            if isinstance(ret, dict) is True: thenowline.append(ret.get('nowline', None))
        if saveretax is False: retkwargs.pop('ax')
        if nowArg is not None and kwargs.get('retnow', False) is True: retkwargs['nowline'] = [item for item in thenowline if item is not None]
        if retkwargs!={}: return retkwargs
