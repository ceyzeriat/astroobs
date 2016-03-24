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

class Target(object):
    """
    Initialises a target object from its right ascension and declination. Optionaly, processes the target for the observatory and date given (refer to :func:`Target.process`).

    Args:
      * ra (str 'hh:mm:ss.s' or float - degrees): the right ascension of the target
      * dec (str '+/-dd:mm:ss.s' or float - degrees): the declination of the target
      * name (str): the name of the target, for display
      * obs (:class:`Observatory`) [optional]: the observatory for which to process the target
      * input_epoch (str): the 'YYYY' year of epoch in which the ra-dec coordinates are given. These coordinates will corrected with precession if the epoch of observatory is different

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      N/A
    """
    def __init__(self, ra, dec, name, input_epoch='2000', obs=None, **kwargs):
        self._raiseError = bool(kwargs.get('raiseError', False))
        if isinstance(ra, (float, int)):
            self._ra = _core.Angle(ra, 'deg')
        else:
            self._ra = _core.Angle(str(ra)+'h')
        self._dec = _core.Angle(str(dec)+'d')
        self.name = str(name)
        self.input_epoch = str(int(input_epoch))
        if obs is not None: self.process(obs=obs, **kwargs)

    def __getitem__(self, key):
        return getattr(self, str(key).lower(), None)

    def _info(self):
        if not hasattr(self,'_ra') or not hasattr(self,'_dec') or not hasattr(self,'name'):
            if raiseIt(_exc.NonTarget, self._raiseError): return
        return "Target: '%s', %ih%im%2.1fs %s%i°%i'%2.1f\"%s" % (self.name, self._ra.hms[0], self._ra.hms[1], self._ra.hms[2], (self._dec.dms[0]>0)*'+', self._dec.dms[0], _core.np.abs(self._dec.dms[1]), _core.np.abs(self._dec.dms[2]), hasattr(self, "_ticked")*(', '+getattr(self, "_ticked", False)*'O'+(not getattr(self, "_ticked", False))*'-'))
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    @property
    def ra(self):
        """
        The right ascension of the target, displayed as tuple (hh, mm, ss)
        """
        ra = self._ra.hms
        return [int(ra[0]), int(ra[1]), ra[2]]
    @ra.setter
    def ra(self, value):
        if raiseIt(_exc.ReadOnly, self._raiseError, "ra"): return

    @property
    def dec(self):
        """
        The declination of the target, displayed as tuple (+/-dd, mm, ss)
        """
        dec = self._dec.dms
        return [int(dec[0]), int(dec[1]), dec[2]]
    @dec.setter
    def dec(self, value):
        if raiseIt(_exc.ReadOnly, self._raiseError, "dec"): return

    @property
    def raStr(self):
        """
        A pretty printable version of the right ascension of the target
        """
        hms = self._ra.hms
        return "%ih%im%2.1fs" % (hms[0], hms[1], hms[2])
    @raStr.setter
    def raStr(self, value):
        if raiseIt(_exc.ReadOnly, self._raiseError, "raStr"): return
    @property
    def decStr(self):
        """
        A pretty printable version of the declination of the target
        """
        dms = self._dec.dms
        return "%s%i°%i'%2.1f\"" % ((dms[0]>0)*'+', dms[0], dms[1], dms[2])
    @decStr.setter
    def decStr(self, value):
        if raiseIt(_exc.ReadOnly, self._raiseError, "dectr"): return

    def _set_RiseSetTransit(self, target, obs, **kwargs):
        """
        Adds to self the attributes set_time, set_az, rise_time, rise_az, transit_az, transit_alt, transit_time of a target given an observatory.
        Set to rise/set attributes to None in case the target does not rise/set
        """
        s1 = obs.date # save initial obs values
        obs.date = obs.dates[0]
        self.rise_time = None
        self.rise_az = None
        self.set_time = None
        self.set_az = None
        try: # try block to catch NeverUp or AlwaysUp errors from pyephem in case of polar region
            self.set_time = obs.next_setting(target)
            obs.date = self.set_time
            target.compute(obs)
            self.set_az = _core.np.rad2deg(target.az)
            self.rise_time = obs.previous_rising(target)
            obs.date = self.rise_time
            target.compute(obs)
            self.rise_az = _core.np.rad2deg(target.az)
        except _core.E.AlwaysUpError:
            self.alwaysUp = True
        except _core.E.NeverUpError:
            self.alwaysUp = False
        if self.rise_time is not None:
            obs.date = self.rise_time
        else:
            obs.date = obs.dates[0]
        self.transit_time = obs.next_transit(target)
        obs.date = self.transit_time
        target.compute(obs)
        self.transit_az = _core.np.rad2deg(target.az)
        self.transit_alt = _core.np.rad2deg(target.alt)
        obs.date = s1 # restore initial obs values

    def process(self, obs, **kwargs):
        """
        Processes the target for the given observatory and date.

        Args:
          * obs (:class:`Observatory`): the observatory for which to process the target

        Kwargs:
          See class constructor

        Raises:
          N/A

        Creates vector attributes:
          * ``airmass``: the airmass of the target
          * ``ha``: the hour angle of the target (degrees)
          * ``alt``: the altitude of the target (degrees - horizon is 0)
          * ``az``: the azimuth of the target (degrees)
          * ``moondist``: the angular distance between the moon and the target (degrees)

        .. note::
          * All previous attributes are vectors related to the time vector of the observatory used for processing, stored under ``dates`` attribute

        Other attributes:
          * ``rise_time``, ``rise_az``: the time (ephem.Date) and the azimuth (degree) of the rise of the target
          * ``set_time``, ``set_az``: the time (ephem.Date) and the azimuth (degree) of the setting of the target
          * ``transit_time``, ``transit_az``: the time (ephem.Date) and the azimuth (degree) of the transit of the target
        
        .. warning::
          * it can occur that the target does not rise or set for an observatory/date combination. In that case, the corresponding attributes will be set to ``None``, i.e. ``set_time``, ``set_az``, ``rise_time``, ``rise_az``. In that case, an additional parameter is added to the Target object: ``Target.alwaysUp`` which is ``True`` if the target never sets and ``False`` if it never rises above the horizon.
        """
        save_date = obs.date # saves the date
        obs.date = obs.dates[0]
        self.airmass = []
        self.ha = []
        self.alt = []
        self.az = []
        self.moondist = []
        targetdb = "star,f|V|G2,%s,%s%s,0.0,%s" % (':'.join(map(str, self.ra)), '-'*(self.dec[0]<0), ':'.join(map(str, map(abs, self.dec))), int(self.input_epoch))
        target = _core.E.readdb(targetdb)
        self._set_RiseSetTransit(target=target, obs=obs, **kwargs)
        for t in range(len(obs.dates)):
            obs.date = obs.dates[t] # forces the obs date for target calculation
            target.compute(obs)
            self.airmass.append(_core.rad_to_airmass(target.alt))
            self.alt.append(target.alt)
            self.az.append(target.az)
            self.ha.append(obs.lst[t] - target.a_ra)
            self.moondist.append(_core.E.separation([self.az[t], self.alt[t]], [_core.np.deg2rad(obs.moon.az[t]), _core.np.deg2rad(obs.moon.alt[t])]))
        # set radec to obs epoch
        self._ra = _core.np.rad2deg(_core.Angle(target.a_ra, unit='rad'))
        self._dec = _core.np.rad2deg(_core.Angle(target.a_dec, unit='rad'))
        obs.date = save_date # sets obs date back
        self.alt = _core.np.rad2deg(self.alt)
        self.az = _core.np.rad2deg(self.az)
        self.ha = _core.np.rad2deg(self.ha)
        self.airmass = _core.np.asarray(self.airmass)
        self.moondist = _core.np.rad2deg(self.moondist)

    def _whenobs(self, obs, fromDate="now", toDate="now+30day", plot=True, ret=False, dday=1, **kwargs):
        """
        Does the calculations for whenobs method
        """
        if fromDate=="now":
            fromDate = _core.E.now()
        else:
            fromDate = _core.cleanTime(fromDate, format='ed')
        if toDate=="now+30day":
            toDate = _core.E.Date(fromDate+30)
        else:
            toDate = _core.cleanTime(toDate, format='ed')
        old_date = obs.date
        dday = max(1, int(dday))
        dates = _core.np.arange(fromDate, toDate, dday)
        retval = []
        for date in dates:
            obs.upd_date(ut_date=_core.E.Date(date), **kwargs)
            # checks for polar night/day
            if obs.sunset is None or obs.sunrise is None: # if polar
                if obs.alwaysDark is True:
                    gooddates = _core.np.ones(len(obs.dates), dtype=bool)
                else:
                    retval.append((0., 0., obs.dates.size*dt, 0., 0., 0., 0.))
                    continue
            else:
                gooddates = ((obs.dates>obs.sunset) & (obs.dates<obs.sunrise))
            dt = (obs.dates[1]-obs.dates[0])*24
            self.process(obs=obs, **kwargs)
            badalt = (self.alt[gooddates]<obs.horizon_obs)
            if obs.sunsetastro is None or obs.sunriseastro is None: # no astro set or rise of target
                badsunsetting = _core.np.ones(gooddates.sum(), dtype=bool)
                badsunrising = _core.np.ones(gooddates.sum(), dtype=bool)
            else:
                badsunsetting = (obs.dates[gooddates]<obs.sunsetastro)
                badsunrising = (obs.dates[gooddates]>obs.sunriseastro)
            badmoon = (self.moondist[gooddates]<obs.moonAvoidRadius)
            # get statistics for target
            sunsettinggoodmoon = ((badsunsetting) & (_core.np.logical_not(badmoon)) & (_core.np.logical_not(badalt)))
            sunsettingbadmoon = ((badsunsetting) & (badmoon) & (_core.np.logical_not(badalt)))
            sunrisinggoodmoon = ((badsunrising) & (_core.np.logical_not(badmoon)) & (_core.np.logical_not(badalt)))
            sunrisingbadmoon = ((badsunrising) & (badmoon) & (_core.np.logical_not(badalt)))
            obsgoodmoon = ((_core.np.logical_not(badsunrising)) & (_core.np.logical_not(badsunsetting)) & (_core.np.logical_not(badalt)) & (_core.np.logical_not(badmoon)))
            obsbadmoon = ((_core.np.logical_not(badsunrising)) & (_core.np.logical_not(badsunsetting)) & (_core.np.logical_not(badalt)) & (badmoon))
            darkbadalt = ((badalt) & (_core.np.logical_not(badsunrising)) & (_core.np.logical_not(badsunsetting)))
            twighlightbadalt = ((badalt) & ((badsunrising) | (badsunsetting)))
            retval.append((obsgoodmoon.sum()*dt, obsbadmoon.sum()*dt, sunsettinggoodmoon.sum()*dt, sunsettingbadmoon.sum()*dt, sunrisinggoodmoon.sum()*dt, sunrisingbadmoon.sum()*dt, darkbadalt.sum()*dt, twighlightbadalt.sum()*dt))
        # set the date back
        obs.upd_date(ut_date=old_date, **kwargs)
        self.process(obs=obs, **kwargs)
        # prepare outputing
        retkeys = ['obs','moon','dusk','duskmoon','dawn','dawnmoon','darklow','twighlightlow']
        retval = _core.np.asarray(retval, dtype=[(key, 'f8') for key in retkeys])
        return dates, retval, retkeys

    def whenobs(self, obs, fromDate="now", toDate="now+30day", plot=True, ret=False, dday=1, **kwargs):
        """
        Processes the target for the given observatory and dat.

        Args:
          * obs (:class:`Observatory`): the observatory for which to process the target
          * fromDate (see below): the start date of the range
          * toDate (see below): the end date of the range
          * plot: whether it plots the diagram
          * ret: whether it returns the values
          * dday: the 

        Kwargs:
          See class constructor
          * legend (bool): whether to add a legend or not, default is ``True``
          * loc: location of the legend, default is 8 (top right), refer to plt.legend
          * ncol: number of columns in the legend, default is 3, refer to plt.legend
          * columnspacing: spacing between columns in the legend, refer to plt.legend
          * lfs: legend font size, default is 11

        Raises:
          N/A

        .. note::
          * ``local_date`` and ``ut_date`` can be date-tuples ``(yyyy, mm, dd, [hh, mm, ss])``, timestamps, datetime structures or ephem.Date instances.
        """
        defaultlegend = True
        dates, retval, retkeys = self._whenobs(obs=obs, fromDate=fromDate, toDate=toDate, plot=plot, ret=ret, dday=dday, **kwargs)
        if plot is True:
            if _core.NOPLOT:
                if raiseIt(_exc.NoPlotMode, self._raiseError): return
            def daymon(t):
                months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                t = str(_core.E.Date(t)).split()[0].split('/')[1:][::-1]
                return t[0]+' '+months[int(t[1])]
            thefig = _core.plt.figure()
            theax = thefig.add_axes([0.09,0.15,0.85,0.8])
            bottombar = _core.np.zeros(dates.size)
            color = {'obs':'#02539C', 'moon':'#02539C', 'twighlightlow':'#AB6E50', 'darklow':'#6E2D0D', 'dusk':'#FACF50', 'duskmoon':'#FACF50', 'dawnmoon':'#A1E6E2', 'dawn':'#A1E6E2'}
            legend = {'obs':'Optimal','twighlightlow':'Low+Dusk/Dawn', 'darklow':'Low+Dark', 'dusk':'Up+Dusk','dawn':'Up+Dawn'}
            hatch = {'duskmoon':'//', 'moon':'//', 'dawnmoon':'//'}
            datestr = [daymon(item) for item in dates]
            for key in retkeys:
                if legend.get(key, '')!='' and kwargs.get('legend', defaultlegend) is True:
                    theax.bar(dates, retval[key], bottom=bottombar, width=0.8+(dday-1)*0.9, color=color[key], hatch=hatch.get(key, ''), edgecolor='k', linewidth=0.0, label=legend.get(key, ''))
                else:
                    theax.bar(dates, retval[key], bottom=bottombar, width=0.8+(dday-1)*0.9, color=color[key], hatch=hatch.get(key, ''), edgecolor='k', linewidth=0.0)
                bottombar += retval[key]
            _core.plt.xticks(dates[0::2]+0.5, datestr[0::2], rotation='vertical')
            theax.bar(dates, _core.np.zeros(dates.size), bottom=0, color='w', hatch='//', edgecolor='k', label='Moon')
            theax.set_xlim([dates[0]-1, dates[-1]+2])
            theax.set_ylabel('Duration (hour)')
            theax.set_title(getattr(self, 'name', self.raStr+' '+self.decStr)+' @ '+getattr(obs, 'name', str(obs.lat)+' '+str(obs.lon)))
            if kwargs.get('legend', defaultlegend) is True:
                l=theax.legend(loc=kwargs.get('loc', 8), frameon=True, ncol=kwargs.get('ncol', 3), columnspacing=kwargs.get('columnspacing', 0.2))
                l.zorder=400
                theax.get_legend().texts[0].set_fontsize(kwargs.get('lfs', 11))
        if ret is not False: return dates, retval

    def plot(self, obs, y='alt', **kwargs):
        """
        Plots the y-parameter vs time diagram for the target at the given observatory and date

        Args:
          * obs (:class:`Observatory`): the observatory for which to plot the target
          * y (object attribute): the y-data to plot

        Kwargs:
          * See class constructor
          * See :func:`Observatory.plot`
          * simpleplt (bool): if ``True``, the observatory plot will not be plotted, default is ``False``
          * color (str or #XXXXXX): the color of the target curve, default is 'k'
          * lw (float): the linewidth, default is 1
        
        Raises:
          N/A
        """
        if _core.NOPLOT:
            if raiseIt(_exc.NoPlotMode, self._raiseError): return
        kwargs['polar'] = False
        return self._plot(obs=obs, y=y, **kwargs)

    def polar(self, obs, **kwargs):
        """
        Plots the sky-view diagram for the target at the given observatory and date

        Args:
          * obs (:class:`Observatory`): the observatory for which to plot the target
          * y (object attribute): the y-data to plot

        Kwargs:
          * See class constructor
          * See :func:`Observatory.plot`
          * See :func:`Target.plot`
        
        Raises:
          N/A
        """
        if _core.NOPLOT:
            if raiseIt(_exc.NoPlotMode, self._raiseError): return
        kwargs['polar'] = True
        return self._plot(obs=obs, **kwargs)

    def _plot(self, obs, y='alt', **kwargs):
        defaultlegend = False
        kwargs['title'] = kwargs.get('title', getattr(self, 'name', self.raStr+' '+self.decStr)+' @ '+getattr(obs, 'name', str(obs.lat)+' '+str(obs.lon)) +' - '+str(obs.localnight).split()[0])
        kwargs['ylabel'] = kwargs.get('ylabel', 'Elevation (°) vs time (UT)')
        saveretax = kwargs.get('retax', False)
        kwargs['retax'] = True
        retkwargs = obs._plot(**kwargs)
        if kwargs.get('polar', False) is False:
            if kwargs.get('legend', defaultlegend) is True:
                retkwargs['ax'].plot(obs.dates, getattr(self, y), kwargs.get('color', 'k'), lw=kwargs.get('lw', 1), label=getattr(self, 'name', self.raStr+' '+self.decStr))
            else:
                retkwargs['ax'].plot(obs.dates, getattr(self, y), kwargs.get('color', 'k'), lw=kwargs.get('lw', 1))
            if kwargs.get('textlbl', False) is True:
                margintxt = int(self.alt.size*0.2)
                retkwargs['ax'].text(obs.dates[:-margintxt][self.alt[:-margintxt].argmax()], self.alt[:-margintxt].max(), getattr(self, 'name', self.raStr+' '+self.decStr))
        else:
            xstuff = (90-self.alt)*_core.np.cos(self.az*_core.np.pi/180+_core.np.pi/2)
            ystuff = (90-self.alt)*_core.np.sin(self.az*_core.np.pi/180+_core.np.pi/2)
            #goodtime = _core.np.hypot(xstuffori, ystuffori) < 90-obs.horizon_obs+float(kwargs.get('ymin_margin', 10)) # when inside the polar plot
            #xstuff = xstuffori[goodtime]
            #ystuff = ystuffori[goodtime]
            if kwargs.get('legend', defaultlegend) is True:
                retkwargs['ax'].plot(xstuff, ystuff, kwargs.get('color', 'k'), lw=kwargs.get('lw', 1), label=getattr(self, 'name', self.raStr+' '+self.decStr))
            else:
                retkwargs['ax'].plot(xstuff, ystuff, kwargs.get('color', 'k'), lw=kwargs.get('lw', 1))
            darktime = ((obs.dates>=obs.sunsetastro) & (obs.dates<=obs.sunriseastro)) # when dark night
            retkwargs['ax'].plot(xstuff[darktime], ystuff[darktime], kwargs.get('color', 'k'), lw=kwargs.get('lw', 1)+2) # plots big lw for good alt target
            bestalt = self.alt.argmax()
            if kwargs.get('textlbl', False) is True:
                retkwargs['ax'].text(xstuff[bestalt], ystuff[bestalt], getattr(self, 'name', self.raStr+' '+self.decStr))
            if kwargs.has_key('gemmenow') is True:
                ret = retkwargs['ax'].plot(xstuff[kwargs['gemmenow']], ystuff[kwargs['gemmenow']], 'ko', ms=4)[0]
                xmoon = (90-obs.moon.alt[kwargs['gemmenow']])*_core.np.cos(obs.moon.az[kwargs['gemmenow']]*_core.np.pi/180+_core.np.pi/2)
                ymoon = (90-obs.moon.alt[kwargs['gemmenow']])*_core.np.sin(obs.moon.az[kwargs['gemmenow']]*_core.np.pi/180+_core.np.pi/2)
                retkwargs['ax'].add_artist(_core.plt.Circle((xmoon, ymoon), obs.moonAvoidRadius, fc='r', alpha=0.3, ec='r', fill=True))
                if kwargs.get('retnow', False) is True: retkwargs['nowline'] = ret
        if kwargs.get('legend', defaultlegend) is True:
            l=retkwargs['ax'].legend(loc=kwargs.get('loc', 8), frameon=True, ncol=kwargs.get('ncol', 3), columnspacing=kwargs.get('columnspacing', 0.2))
            l.zorder=400
            retkwargs['ax'].get_legend().texts[0].set_fontsize(kwargs.get('lfs', 11))
        if saveretax is False: retkwargs.pop('ax')
        if retkwargs!={}: return retkwargs
