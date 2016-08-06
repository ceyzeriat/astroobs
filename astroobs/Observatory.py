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

from .ObservatoryList import ObservatoryList
from .Moon import Moon

class Observatory(_core.E.Observer, object):
    """
    Defines an observatory from which the ephemeris of the twilights or a night-sky target are processed. The *night-time* is base on the given date. It ends at the next sunrise and starts at the sunset preceeding this next sunrise.

    Args:
      * obs (str): id of the observatory to pick from the observatories database OR the name of the custom observatory (in that case, ``long``, ``lat``, ``elevation``, ``timezone`` must also be given, ``temp``, ``pressure``, ``moonAvoidRadius`` are optional)
      * local_date (see below): the date of observation in local time
      * ut_date (see below): the date of observation in UT time
      * horizon_obs (float - degrees): minimum altitude at which a target can be observed, default is 30 degrees altitude
      * epoch (str): the 'YYYY' year in which all ra-dec coordinates are converted

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``
      * fig: TBD

    Raises:
      * NameError: if a mandatory input parameter is missing
      * KeyError: if the observatory ID does not exist
      * KeyError: if the twilight keyword is unknown
      * Exception: if the observatory object has no date

    .. note::
      * For details on ``local_date`` and ``ut_date``, refer to :func:`Observatory.upd_date`
      * For details on other input parameters, refer to :func:`ObservatoryList.add`
      * The :class:`Observatory` automatically creates and manages a :class:`Moon` target under ``moon`` attribute
      * If ``obs`` is the id of an observatory to pick in the database, the user can still provide ``temp``, ``pressure``, ``moonAvoidRadius`` attributes which will override the database default values
      * ``horizon`` attribute is in radian

    Main attributes:
      * ``localnight``: gives the local midnight time in local time (YYYY, MM, DD, 23, 59, 59)
      * ``date``: gives the local midnight time in UT time
      * ``dates``: is a vector of Dublin Julian Dates. Refer to :func:`process_obs`
      * ``lst``: the local sidereal time corresponding to each ``dates`` element
      * ``localTimeOffest``: gives the shift in days between UT and local time: local=UT+localTimeOffest
      * ``moon``: points to the :class:`Moon` target processed for the given observatory and date
    Twilight attributes:
      * For the next three attributes, ``XXX`` shall be replaced by {'' (blank), 'civil', 'nautical', 'astro'} for, respectively, horizon, -6, -12, and -18 degrees altitude
      * ``sunriseXXX``: gives the sunrise time for different twilights, in Dublin Julian Dates. e.g.: ``observatory.sunrise``
      * ``sunsetXXX``: gives the sunset time for different twilights, in Dublin Julian Dates. e.g.: ``observatory.sunsetcivil``
      * ``len_nightXXX``: gives the night duration for different twilights (between corresponding sunset and sunrise), in hours. e.g.: ``observatory.len_nightnautical``

    .. warning::
      * it can occur that the Sun, the Moon or a target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``

    >>> import astroobs.obs as obs
    >>> o = obs.Observatory('ohp', local_date=(2015,3,31,23,59,59))
    >>> o
    <ephem.Observer date='2015/3/31 21:59:59' epoch='2000/1/1 12:00:00'
    lon=5:42:48.0 lat=43:55:51.0 elevation=650.0m horizon=-0:49:04.8
    temp=15.0C pressure=1010.0mBar>
    >>> o.moon
    Moon - phase: 89.2%
    >>> print(o.sunset, '...', o.sunrise, '...', o.len_night)
    2015/3/31 18:08:40 ... 2015/4/1 05:13:09 ... 11.0746939826
    >>> import ephem as E
    >>> print(E.Date(o.sunsetastro+o.localTimeOffest), '...', E.Date(
            o.sunriseastro+o.localTimeOffest), '...', o.len_nightastro)
    2015/3/31 21:43:28 ... 2015/4/1 05:38:26 ... 7.91603336949
    """
    def __init__(self, obs, long=None, lat=None, elevation=None, timezone=None, temp=None, pressure=None, moonAvoidRadius=None, local_date=None, ut_date=None, horizon_obs=None, dataFile=None, epoch='2000', **kwargs):
        super(Observatory, self).__init__() # first init
        self._raiseError = bool(kwargs.pop('raiseError', False))
        if long is None and lat is None and elevation is None and timezone is None: # gave directly an obsid, supposely
            obslist = ObservatoryList(dataFile=dataFile, **kwargs)
            obs = str(obs).lower()
            if obs in obslist.obsids: # if correct id
                for k, v in obslist.obsdic[obs].items(): # copy the site info to self
                    setattr(self, k, v)
                self.id = obs
            else: # if not correct id
                if _exc.raiseIt(_exc.UnknownObservatory, self._raiseError, obs): return
        elif long is not None and lat is not None and elevation is not None and timezone is not None: # gave the details of a valid observatory
            self.name = str(obs)
            self.timezone = str(timezone)
            self.elevation = float(elevation)
            # checks the type of long and lat
            if isinstance(long, (float, int)):
                self.long = _core.np.deg2rad(long)
            else:
                self.long = _core.E.degrees(long)
            if isinstance(lat, (float, int)):
                self.lat = _core.np.deg2rad(lat)
            else:
                self.lat = _core.E.degrees(lat)
        else: # a parameter is missing
            if _exc.raiseIt(_exc.UncompleteObservatory, self._raiseError, obs): return
        # overwrite observatory value
        if temp is not None: self.temp = float(temp)
        if pressure is not None: self.pressure = float(pressure)
        if moonAvoidRadius is not None: self.moonAvoidRadius = float(moonAvoidRadius)
        # checks if values exist and sets default if not
        if not hasattr(self, 'temp'): self.temp = 15.0
        if not hasattr(self, 'pressure'): self.pressure = 1010.0
        if not hasattr(self, 'moonAvoidRadius'): self.moonAvoidRadius = 0.25
        epoch = str(int(epoch)) # set epoch
        if epoch == '2000':
            self.epoch = _core.E.J2000
        elif epoch == '1950':
            self.epoch = _core.E.B1950
        else:
            self.epoch = epoch
        self.horizon = -_core.np.sqrt(2*self.elevation/_core.E.earth_radius)
        if horizon_obs is None:
            self.horizon_obs = 30. # default value
        else:
            self.horizon_obs = float(horizon_obs)
        # initialise the date
        self.upd_date(local_date=local_date, ut_date=ut_date, force=True, **kwargs)


    def _calc_sunRiseSet(self, mode='', **kwargs):
        """
        Processes sunrise, sunset in UTC and night duration in hour and adds info to the object as attributes
        mode can be: '' (horizon), 'astro' (-18 degrees), 'nautical' (-12 degrees),'civil' (-6 degrees)

        assumption: self.date is local midnight of the observation date and is expressed in UT
        """
        horizs = {'':self.horizon, 'astro':-0.314159, 'nautical':-0.2094395, 'civil':-0.104719} # 18, 12 and 6 degrees in radian
        mode = str(mode).lower()
        if mode not in horizs.keys():
            if _exc.raiseIt(_exc.UnknownTwilight, self._raiseError, mode): return
        s1, s2 = self.horizon, self.date # save initial obs values
        self.horizon = horizs[mode.lower()] # set horizon from mode
        # init in case of error
        setattr(self, "sunrise"+mode.lower(), None)
        setattr(self, "sunset"+mode.lower(), None)
        setattr(self, "len_night"+mode.lower(), 0.)
        try: # try block to catch NeverUp or AlwaysUp errors from pyephem in case of polar region
            v = self.next_rising(_core.E.Sun())
            setattr(self, "sunrise"+mode.lower(), v) # adds property sunrise of mode
            self.date = v
            setattr(self, "sunset"+mode.lower(), self.previous_setting(_core.E.Sun())) # adds property sunset of mode
            setattr(self, "len_night"+mode.lower(), (getattr(self, "sunrise"+mode.lower()) - getattr(self, "sunset"+mode.lower()))*24)
        except _core.E.AlwaysUpError:
            self.alwaysDark = False
        except _core.E.NeverUpError:
            self.alwaysDark = True
        self.horizon, self.date = s1, s2 # restore initial obs values


    def upd_date(self, ut_date=None, local_date=None, force=False, **kwargs):
        """
        Updates the date of the observatory, and re-process the observatory parameters if the date is different.

        Args:
          * ut_date (see below): the date of observation in UT time
          * local_date (see below): the date of observation in local time
          * force (bool): if ``False``, the observatory is re-processed only if the date changed

        Kwargs:
          See :class:`Observatory`

        Raises:
          * KeyError: if the twilight keyword is unknown
          * Exception: if the observatory object has no date

        Returns:
          ``True`` if the date was changed, otherwise ``False``

        .. note::
          * ``local_date`` and ``ut_date`` can be date-tuples ``(yyyy, mm, dd, [hh, mm, ss])``, timestamps, datetime structures or ephem.Date instances.
          * If both are given, ``ut_date`` has higher priority
          * If neither of those are given, the date is automatically set to *tonight* or *now* (whether the sun has already set or not)
        """
        stored_date = getattr(self, 'localnight', _core.datetime(2000, 1, 1))
        s1 = self.date # saves initiprocess_obsal date value
        # set the local_date to this night's sunset time in local time so we can get the local day/month/year
        if local_date is None and ut_date is None: # default set to tonight midnight if date not provided
            self.date = _core.E.now() # takes the now for temporary calculation
            try: # are we in a polar region ?
                self.date = _core.E.Date(self.next_rising(_core.E.Sun()))
                local_date = _core.convertTime(self.previous_setting(_core.E.Sun()), self.timezone, 'utc', format='dt')
            except (_core.E.AlwaysUpError, _core.E.NeverUpError): # yes sire
                if _core.convertTime(_core.E.now(), self.timezone, 'utc', format='dt').hour<12: # yest
                    local_date = _core.E.Date(_core.convertTime(_core.E.now(), self.timezone, 'utc', format='ed')-1).datetime()
                else: # today
                    local_date = _core.convertTime(_core.E.now(), self.timezone, 'utc', format='dt')
        elif ut_date is not None: # if given ut date
            local_date = _core.convertTime(ut_date, self.timezone, 'utc', format='dt')
        else: # if given local date
            local_date = _core.cleanTime(local_date, format='dt')
        # check if the date has changed
        if stored_date.year==local_date.year and stored_date.month==local_date.month and stored_date.day==local_date.day and force is False: # didn't change
            self.date = s1 # set initial value back
            return False
        else: # the date has changed
            self.localTimeOffest = _core.convertTime(_core.E.now(), self.timezone, 'utc', format='ed')-_core.E.now()
            self.localnight = local_date.replace(hour=23, minute=59, second=59) # midnight in local time
            self.date = _core.convertTime(self.localnight, 'utc', self.timezone, format='ed') # midnight in UT time
            self.process_obs(**kwargs)
            return True


    def process_obs(self, pts=200, margin=15, fullhour=False, **kwargs):
        """
        Processes all twilights as well as moon rise, set and position through night for the given observatory and date.
        Creates the vector ``observatory.dates`` which is the vector containing all timestamps at which the moon and the targets will be processed.

        Args:
          * pts (int) [optional]: the size of the ``dates`` vector, whose elements are linearly spaced in time
          * margin (float - minutes) [optional]: the margin between the first element of the vector ``dates`` and the sunset, and between the sunrise and its last element
          * fullhour (bool) [optional]: if ``True``, then the vector ``dates`` will start and finish on the first full hour preceeding sunset and following sunrise

        Kwargs:
          See :class:`Observatory`

        Raises:
          * KeyError: if the twilight keyword is unknown
          * Exception: if the observatory object has no date

        .. note::
          In case the observatory is in polar regions where the sun does not alway set and rise everyday, the first and last elements of the ``dates`` vector are set to local midday right before and after the local midnight of the observation date. e.g.: 24h night centered on the local midnight.
        """
        def set_data_range(sunset, sunrise, numdates, margin=15, fullhour=False):
            """Returns a numpy array of numdates dates linearly spaced in time, from margin minutes before sunset to margin minutes after sunrise if fullhour is False, and from the previous full hour before sunset to next full hour after sunrise if fullhour is True."""
            if fullhour:
                ss = _core.E.Date(int(sunset*24)/24.)
                sr = _core.E.Date(int(sunrise*24+1)/24.)
            else:
                ss = _core.E.Date(float(sunset) - margin*_core.E.minute)
                sr = _core.E.Date(float(sunrise) + margin*_core.E.minute)
            return _core.np.linspace(ss, sr, int(numdates))
        if not hasattr(self, "date"):
            if _exc.raiseIt(_exc.NoObservatoryDate, self._raiseError, obs): return
        self.date = _core.cleanTime(self.date, format='ed')
        for mode in ['','astro','nautical','civil']: # gets sunrise and sunsets for all modes
            self._calc_sunRiseSet(mode=mode, **kwargs)
        if self.sunset is not None and self.sunrise is not None:
            self.dates = set_data_range(sunset=self.sunset, sunrise=self.sunrise, numdates=pts, margin=margin, fullhour=fullhour) # gets linearly spaced dates along the night
        else: # no sunrise or sunset, observatory in polar regions
            startnight = _core.convertTime(self.localnight.replace(hour=12, minute=0, second=0), 'utc', self.timezone, format='ed')
            endnight = _core.convertTime(_core.E.Date(_core.E.Date(self.localnight)+1).datetime().replace(hour=11, minute=59, second=59), 'utc', self.timezone, format='ed')
            self.dates = set_data_range(sunset=startnight, sunrise=endnight, numdates=pts, margin=0, fullhour=False) # gets linearly spaced dates along the night
        # computes the lst
        s1 = self.date
        self.lst = []
        for d in self.dates:
            self.date = d
            self.lst.append(self.sidereal_time())
        self.lst = _core.np.asarray(self.lst)*12/_core.np.pi # get radians to hours
        self.date = s1
        # computes the Moon
        self.moon = Moon(obs=self)


    @property
    def nowArg(self):
        """
        Returns the index of *now* in the ``observatory.dates`` vector, or None if *now* is out of its bounds (meaning the observation is not taking place now)

        >>> import astroobs.obs as obs
        >>> import ephem as E
        >>> o = obs.Observatory('ohp')
        >>> plt.plot(o.dates, o.moon.alt, 'k-')
        >>> now = o.nowArg
        >>> if now is not None:
        >>>     plt.plot(o.dates[now], o.moon.alt[now], 'ro')
        >>> else:
        >>>     plt.plot([E.now(), E.now()], [o.moon.alt.min(),o.moon.alt.max()], 'r--')
        """
        now = _core.E.now()
        deltadates = (self.dates[1]-self.dates[0])/2.
        if now<self.dates[0]-deltadates or now>self.dates[-1]+deltadates: return None
        return (_core.np.abs(self.dates-_core.E.now())).argmin()
    @nowArg.setter
    def nowArg(self, value):
        if _exc.raiseIt(_exc.ReadOnly, self._raiseError, "nowArg"): return


    def plot(self, **kwargs):
        """
        Plots the observatory diagram

        Kwargs:
          * See :class:`Observatory`
          * See :func:`Observation.plot`

        Raises:
          N/A
        """
        if _core.NOPLOT:
            if _exc.raiseIt(_exc.NoPlotMode, self._raiseError): return
        return self._plot(**kwargs)

    def polar(self, **kwargs):
        """
        Plots the observatory diagram in polar coordinates

        Kwargs:
          * See :class:`Observatory`
          * See :func:`Observation.plot`

        Raises:
          N/A
        """
        if _core.NOPLOT:
            if _exc.raiseIt(_exc.NoPlotMode, self._raiseError): return
        kwargs['polar'] = True
        return self._plot(**kwargs)

    def _plot(self, **kwargs):
        if kwargs.get('fignum', None) is None and kwargs.get('fig', None) is None and kwargs.get('axnum', None) is None and kwargs.get('ax', None) is None: # no fig and no ax given, need to create
            thefig = _core.plt.figure()
        elif kwargs.get('fignum', None) is not None:
            thefig = _core.plt.figure(kwargs['fignum'])
        elif kwargs.get('fig', None) is None and kwargs.get('ax', None) is not None:
            thefig = _core.plt.figure(kwargs['ax'].figure.number)
        else:
            thefig = kwargs['fig']
        if kwargs.get('axnum', None) is None and kwargs.get('ax', None) is None:
            if kwargs.get('polar', False) is True:
                theax = thefig.add_subplot(111, aspect='equal')
            else:
                theax = thefig.add_axes([0.1,0.1,0.8,0.8])
        elif kwargs.get('axnum', None) is not None:
            theax = thefig.axes[kwargs['ax']]
        else:
            theax = kwargs['ax']
        retkwargs = {}
        if kwargs.get('retfignum', False) is True: retkwargs['fignum'] = thefig.number
        if kwargs.get('retaxnum', False) is True: retkwargs['axnum'] = thefig.axes.index(theax)
        if kwargs.get('retfig', False) is True: retkwargs['fig'] = thefig
        if kwargs.get('retax', False) is True: retkwargs['ax'] = theax
        if kwargs.get('simpleplt', False) is not False:
            if retkwargs!={}:
                return retkwargs
            else:
                return
        if kwargs.get('polar', False) is True:
            axlim = 90-self.horizon_obs+float(kwargs.get('ymin_margin', 10))
            _core.plt.xticks([0], ["S"])
            _core.plt.yticks([0], ["E"])
            theax.text(axlim+2, -2, 'O')
            _core.plt.sca(theax)
            theax.add_artist(_core.plt.Circle((0,0), axlim, fc='#B3B3B3', ec='none', fill=True))
            theax.add_artist(_core.plt.Circle((0,0), 90-self.horizon_obs, fc='w', ec='none', fill=True))
            for alt in _core.np.arange(self.horizon_obs, 91, 10):
                theax.add_artist(_core.plt.Circle((0,0), 90-alt, fc='none', ec='k', ls='dotted', alpha=0.3, fill=False))
                if alt==90: continue
                theax.text(1, 89-alt, int(alt), alpha=0.5)
            for az in _core.np.arange(0, _core.np.pi, _core.np.pi/4):
                theax.plot([axlim*_core.np.cos(az), -axlim*_core.np.cos(az)], [axlim*_core.np.sin(az), -axlim*_core.np.sin(az)], 'k:', alpha=0.3)
            n, radii = 200, [axlim, 200]
            theta = _core.np.linspace(0, 2*_core.np.pi, n, endpoint=True)
            xs = _core.np.outer(radii, _core.np.cos(theta))
            ys = _core.np.outer(radii, _core.np.sin(theta))
            xs[1,:] = xs[1,::-1]
            ys[1,:] = ys[1,::-1]
            theax.fill(_core.np.ravel(xs), _core.np.ravel(ys), color='w', edgecolor='none', zorder=300)
            theax.add_artist(_core.plt.Circle((0,0), axlim, ec='k', fill=False, zorder=301))
            theax.plot(0, _core.np.sign(self.lat)*(90-_core.np.abs(self.lat)*180/_core.np.pi), 'k*')
            theax.set_ylim([-axlim,axlim])
            theax.set_xlim([-axlim,axlim])
        else:
            # set min and max on y axis to most min and most max of any plot-able parameter, or ylim
            minmin, maxmax = theax.set_ylim(kwargs.get('ylim', [-180, 360]))
            # if polar night
            if (self.sunrise is None or self.sunset is None) and getattr(self, 'alwaysDark', False) is True:
                bgcolor = 'w'
            else:
                bgcolor = '#04031C'
            dt = float(kwargs.get('dt', 1.))
            # set up t0 default
            if self.sunset is not None and self.sunrise is not None:
                if self.sunsetastro is not None:
                    start_default = self.sunsetastro
                elif self.sunsetnautical is not None:
                    start_default = self.sunsetnautical
                elif self.sunsetcivil is not None:
                    start_default = self.sunsetcivil
                elif self.sunset is not None:
                    start_default = self.sunset
            else:
                start_default = self.dates[0]
            # set up t0
            lst1 = self.lst[-1]
            if self.lst[-1]<self.lst[0]: lst1 += 24
            if kwargs.get('time', '').lower()!='lst':
                t0 = min(max(float(kwargs.get('t0', start_default)), self.dates[0]), self.dates[-1])
            else:
                start_default = self.lst[0]+_core.np.median(_core.np.diff(self.lst[:4]))*(start_default-self.dates[0])/(self.dates[1]-self.dates[0])
                t0lst = min(max(float(kwargs.get('t0', start_default)), self.lst[0]), lst1)
                t0 = self.dates[0] + (t0lst - self.lst[0])/_core.np.median(_core.np.diff(self.lst[:4]))*(self.dates[1]-self.dates[0])
            # prepare x-axis and ticks
            xaxisvalues = _core.np.r_[_core.np.arange(t0, self.dates[0], -dt/24.)[::-1], _core.np.arange(t0, self.dates[-1], dt/24.)[1:]]
            if kwargs.get('time', '').lower()=='loc':
                xaxisvaluesstr = [str(_core.E.Date(item+self.localTimeOffest)).split()[1][:-3] for item in xaxisvalues]
                if kwargs.get('retxdisp', 'False') is True: retkwargs['xdisp'] = [self.dates[0]+self.localTimeOffest, self.dates[-1]+self.localTimeOffest]
            elif kwargs.get('time', '').lower()=='lst':
                dtlst = dt*(lst1-self.lst[0])/24./(self.dates[-1]-self.dates[0])
                lst = _core.np.r_[_core.np.arange(t0lst, self.lst[0], -dtlst)[::-1], _core.np.arange(t0lst, lst1, dtlst)[1:]]
                xaxisvaluesstr = [str(int(item)).zfill(2)+':'+str(int((item%1)*60)).zfill(2) for item in lst]
                if kwargs.get('retxdisp', 'False') is True: retkwargs['xdisp'] = [self.lst[0], lst1]
            else:            
                xaxisvaluesstr = [str(_core.E.Date(item)).split()[1][:-3] for item in xaxisvalues]
                if kwargs.get('retxdisp', 'False') is True: retkwargs['xdisp'] = [self.dates[0], self.dates[-1]]
                kwargs['time'] = 'UT'
            # prepare background
            theax.add_patch(_core.Rectangle((self.dates[0], minmin), self.dates[-1]-self.dates[0], maxmax, facecolor=bgcolor, edgecolor=bgcolor))
            if self.sunset is not None and self.sunrise is not None:
                theax.add_patch(_core.Rectangle((self.sunset, minmin), self.sunrise-self.sunset, maxmax, facecolor='#1814A3', edgecolor='#1814A3'))
            if self.sunsetcivil is not None and self.sunrisecivil is not None:
                theax.add_patch(_core.Rectangle((self.sunsetcivil, minmin), self.sunrisecivil-self.sunsetcivil, maxmax, facecolor='#6F6BE8', edgecolor='#6F6BE8'))
            if self.sunsetnautical is not None and self.sunrisenautical is not None:
                theax.add_patch(_core.Rectangle((self.sunsetnautical, minmin), self.sunrisenautical-self.sunsetnautical, maxmax, facecolor='#C1BFF2', edgecolor='#C1BFF2'))
            if self.sunsetastro is not None and self.sunriseastro is not None:
                theax.add_patch(_core.Rectangle((self.sunsetastro, minmin), self.sunriseastro-self.sunsetastro, maxmax, facecolor='w', edgecolor='w'))
            theax.set_xlim(kwargs.get('xlim', [self.dates[0], self.dates[-1]]))
            if 'ylim' in kwargs.keys():
                theax.set_ylim(kwargs['ylim'])
            else:
                theax.set_ylim([self.horizon_obs-float(kwargs.get('ymin_margin', 10)), 90])
                theax.add_patch(_core.Rectangle((self.dates[0], minmin), self.dates[-1]-self.dates[0], self.horizon_obs-minmin, facecolor='k', edgecolor='None', alpha=0.3))
            _core.plt.xticks(xaxisvalues, xaxisvaluesstr, rotation='horizontal', size='10')
            theax.grid(True)
            theax.set_xlabel(kwargs.get('xlabel', 'Time ('+kwargs.get('time', 'UT').upper()+')'))
            theax.set_ylabel(kwargs.get('ylabel', 'Elevation (°)'))
            if kwargs.get('now') is True and self.nowArg is not None:
                thenowline = theax.plot([_core.E.now(), _core.E.now()], theax.get_ylim(), 'r-')[0]
            else:
                thenowline = None
        theax.set_title(kwargs.get('title', getattr(self, 'name', str(self.lat)+' '+str(self.lon))+' - '+str(self.localnight).split()[0]))
        if kwargs.get('retnow', False) is True and kwargs.get('polar', False) is False: retkwargs['nowline'] = [thenowline] # if polar, we get the nowline from each item
        if retkwargs!={}: return retkwargs
