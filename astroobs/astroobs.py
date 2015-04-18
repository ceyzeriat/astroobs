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

import _core

_obsDataFile = './obsData.txt'

class ObservatoryList(object):
    """
    Deals with the observatory database

    Add, modify, or remove an observatory from the database
    Output 
    """
    def __init__(self, dataFile=None):
        if dataFile is not None:
            self.dataFile = dataFile
        else:
            try:
                this_dir, this_filename = _core.os.path.split(__file__)
                self.dataFile = _core.os.path.join(this_dir, _obsDataFile[_obsDataFile.find('/')+1:])
            except:
                self.dataFile = _obsDataFile
        self._load()

    def _load(self):
        """
        Loads the list of observatories from the database using dataFile property
        """
        self.heads = [item.strip() for item in open(self.dataFile).readlines() if item.strip()[:7]=='#heads#'][0][7:]
        self.lines = [item.strip() for item in open(self.dataFile).readlines() if (item.strip()[:1]!='#' and item.strip()!="")]
        self._wholefile = [item.strip() for item in open(self.dataFile).readlines()]
        self.obsids = [item.strip().split(';')[0].lower() for item in open(self.dataFile).readlines() if (item.strip()[:1]!='#' and item.strip()!="")]
        allsplitobs = [item.split(';') for item in self.lines]
        self.obsdic = {}
        for item in allsplitobs:
            try:
                self.obsdic.update({item[0]:{'name':str(item[1]),'long':_core.E.degrees(item[2]),'lat':_core.E.degrees(item[3]),'elevation':float(item[4]),'temp':float(item[5]),'pressure':float(item[6]),'timezone':str(item[7]),'moonAvoidRadius':float(item[8])}})
            except:
                raise KeyError, "Missing parameter for '%s' (obsid '%s')" % (item[1], item[0])

    def _info(self):
        return "List of %s observatories" % (len(self.obsids))
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    def __getitem__(self, key):
        return self.obsdic[key]

    def add(self, obsid, name, long, lat, elevation, timezone, temp=15.0, pressure=1010.0, moonAvoidRadius=0):
        """
        Adds an observatory to the observatories database.

        long: longitude string 'ddd:mm:ss.s' - East is positive, West is negative
        lat: latitude string '+dd:mm:ss.s' - North is Positive, South is negative
        elevation: elevation (meter)
        timezone: string like 'America/Santiago'
        temp: temperature (celcius)
        pressure: pressure (hPa)
        moonAvoidRadius: radius of forbiden circle around the moon (degree)
        """
        if str(obsid).lower() in self.obsids:
            print "\033[31mThe observatory ID provided already exists.\033[39m"
        else:
            f = open(self.dataFile, 'a')
            newobs = '\n%s;%s;%s;%s;%s;%s;%s;%s;%s' % (str(obsid).lower(), name, long, lat, elevation, temp, pressure, timezone, moonAvoidRadius)
            f.write(newobs)
            f.close()
            self._load()

    def rem(self, obsid):
        """
        Removes an observatory from the observatories database.
        """
        if str(obsid).lower() not in self.obsids:
            print "\033[31mThe observatory ID provided was not found.\033[39m"
        else:
            newlines = '\n'.join([item.strip() for item in self._wholefile if item.split(';')[0].lower()!=str(obsid).lower()])
            f = open(self.dataFile, 'w')
            f.writelines(newlines)
            f.close()
            self._load()

    def mod(self, obsid, name, long, lat, elevation, timezone, temp=15.0, pressure=1010.0, moonAvoidRadius=0):
        """
        Modifies an observatory in the observatories database.

        cf 'add' method for further details
        """
        if str(obsid).lower() not in self.obsids:
            print "\033[31mThe observatory ID was not found.\033[39m"
        else:
            newobs = '\n%s;%s;%s;%s;%s;%s;%s;%s;%s' % (str(obsid).lower(), name, long, lat, elevation, temp, pressure, timezone, moonAvoidRadius)
            newlines = '\n'.join([item.strip() for item in self._wholefile if item.split(';')[0].lower()!=str(obsid).lower()])
            newlines += newobs
            f = open(self.dataFile, 'w')
            f.writelines(newlines)
            f.close()
            self._load()

    def nameList(self):
        """
        Returns the list of the (obs id, observatory name) in the alphabetical order of column 'observatory name'.
        """
        obsorder = []
        names = _core.np.asarray([item.split(';')[1] for item in self.lines])
        ids = _core.np.asarray([item.split(';')[0] for item in self.lines])
        namesorted = _core.np.argsort(names)
        return zip(ids[namesorted], names[namesorted])


class Observatory(_core.E.Observer, object):
    """
    Defines an observatory

    obs can be:
    - an observatory id is the obs is in the database (input parameters long, lat, elevation, and timezone will be ignored)
    - an observatory name: long, lat, elevation and timezone are mandatory inputs

    long: longitude in 'ddd:mm:ss.s' or decimal degrees - West is positive, East is negative
    lat: latitude in 'dd:mm:ss.s' or decimal degrees - North is Positive, South is negative
    elevation: elevation (m)
    timezone: strin to describe the timezone, case sensitive e.g.: 'Europe/Paris'
    temp: temperature (celcius)
    pressure: pressure (hPa)
    moonAvoidRadius: radius of forbiden circle around the moon (degrees)
    local_date, ut_date: the date of observation
    horizon_obs: minimum observe-able elevation (degree)
    """
    def __init__(self, obs, long=None, lat=None, elevation=None, timezone=None, temp=None, pressure=None, moonAvoidRadius=None, local_date=None, ut_date=None, horizon_obs=None, dataFile=None):
        _core.E.Observer.__init__(self) # first init

        obslist = ObservatoryList(dataFile=dataFile)

        if long is None and lat is None and elevation is None and timezone is None: # gave directly an obsid, supposely
            if str(obs).lower() in obslist.obsids: # if correct id
                for k, v in obslist.obsdic[str(obs).lower()].items(): # copy the site info to self
                    setattr(self, k, v)
            else: # if not correct id
                raise KeyError, "Could not find observatory id %s in database" % (str(obs).lower())
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
            raise Exception, "One or more input parameter missing. All 'long', 'lat', 'elevation', and 'timezone' are mandatory."
        # overwrite observatory value
        if temp is not None: self.temp = float(temp)
        if pressure is not None: self.pressure = float(pressure)
        if moonAvoidRadius is not None: self.moonAvoidRadius = float(moonAvoidRadius)
        # checks if values exist
        if not hasattr(self, 'temp'): self.temp = 15.0
        if not hasattr(self, 'pressure'): self.pressure = 1010.0
        if not hasattr(self, 'moonAvoidRadius'): self.moonAvoidRadius = 0.
        self.epoch = _core.E.J2000 # set epoch
        self.horizon = -_core.np.sqrt(2*self.elevation/_core.E.earth_radius)
        if horizon_obs is None:
            self.horizon_obs = self.horizon
        else:
            self.horizon_obs = _core.np.deg2rad(horizon_obs)
        # initialise the date
        self.upd_date(local_date=local_date, ut_date=ut_date, force=True)


    def _calc_sunRiseSet(self, mode=''):
        """
        Processes sunrise, sunset in UTC and night duration in hour and adds info to the object as attributes
        mode can be: '' (horizon), 'astro' (-18 degrees), 'nautical' (-12 degrees),'civil' (-6 degrees)

        assumption: self.date is local midnight of the observation date and is expressed in UT
        """
        horizs = {'':self.horizon, 'astro':-0.314159, 'nautical':-0.2094395, 'civil':-0.104719} # 18, 12 and 6 degrees
        if mode.lower() not in horizs.keys(): raise KeyError, "Unknown twilight %s" % mode # checks for mode
        s1, s2 = self.horizon, self.date # save initial obs values
        self.horizon = horizs[mode.lower()] # set horizon from mode
        v = self.next_rising(_core.E.Sun())
        setattr(self, "sunrise"+mode.lower(), v) # adds property sunrise of mode
        self.date = v
        setattr(self, "sunset"+mode.lower(), self.previous_setting(_core.E.Sun())) # adds property sunset of mode
        setattr(self, "len_night"+mode.lower(), (getattr(self, "sunrise"+mode.lower()) - getattr(self, "sunset"+mode.lower()))*24)
        self.horizon, self.date = s1, s2 # restore initial obs values



    def upd_date(self, ut_date=None, local_date=None, force=False):
        """
        Updates the date and time to "midnight" on ut_date day or alternatively local_date day
        object.obsnight gives the midnight datetime in local time
        object.date gives the local midnight in UT
        object.localTimeOffest gives the offset between local and UT times (negative to the West), in days

        force = True forces the recalculation of the date

        returns False if the date did not change since last upd_date call and True if it did
        """
        stored_date = getattr(self, 'obsnight', _core.datetime(2000, 1, 1))
        s1 = self.date # saves initial date value
        self.localTimeOffest = _core.convertTime(_core.E.now(), self.timezone, 'utc', format='ed')-_core.E.now()
        # set the local_date to this night's sunset time in local time so we can get the local day/month/year
        if local_date is None and ut_date is None: # default set to tonight midnight if date not provided
            self.date = _core.E.now() # takes the now for temporary calculation
            self.date = _core.E.Date(self.next_rising(_core.E.Sun()))
            local_date = _core.convertTime(self.previous_setting(_core.E.Sun()), self.timezone, 'utc', format='dt')
        elif ut_date is not None: # if given ut date
            local_date = _core.convertTime(ut_date, self.timezone, 'utc', format='dt')
        else: # if given local date
            local_date = _core.cleanTime(local_date, format='dt')
        # check if the date has changed
        if stored_date.year==local_date.year and stored_date.month==local_date.month and stored_date.day==local_date.day and force is False: # didn't change
            self.date = s1 # set initial value back
            return False
        else: # the date has changed
            self.obsnight = _core.datetime(local_date.year, local_date.month, local_date.day, 23, 59, 59) # midnight in local time
            self.date = _core.convertTime(self.obsnight, 'utc', self.timezone, format='ed') # midnight in UT time
            self.process_obs()
            return True


    def process_obs(self, pts=200, margin=15, fullhour=False):
        """
        Processes all twilights as well as moon rise, set and position through night
        All dates in UT
        """
        def set_time(dtime):
            """Sets time to nice rounded value"""
            y, m ,d, hh, mm, ss = dtime.tuple()
            return _core.E.Date(_core.datetime(y, m , d, hh, int(round(mm)), 0))
        def set_data_range(sunset, sunrise, numdates, margin=15, fullhour=False):
            """Returns a numpy array of numdates dates linearly spaced in time, from margin minutes before sunset to margin minutes after sunrise if fullhour is False, and from the previous full hour before sunset to next full hour after sunrise if fullhour is True."""
            if fullhour:
                ss = _core.E.Date(int(sunset*24)/24.)
                sr = _core.E.Date(int(sunrise*24+1)/24.)
            else:
                ss = set_time(_core.E.Date(float(sunset) - margin*_core.E.minute))
                sr = set_time(_core.E.Date(float(sunrise) + margin*_core.E.minute))
            return _core.np.linspace(ss, sr, numdates)
        if not hasattr(self, "date"): raise Exception, "No date specified, 'date' attribute must exist as ephem.date" # checks if date exists
        self.date = _core.cleanTime(self.date, format='ed')
        for mode in ['','astro','nautical','civil']: # gets sunrise and sunsets for all modes
            self._calc_sunRiseSet(mode=mode)
        self.dates = set_data_range(sunset=self.sunset, sunrise=self.sunrise, numdates=pts, margin=margin, fullhour=fullhour) # gets linearly spaced dates along the night
        self.moon = Moon(obs=self)


    @property
    def nowArg(self):
        """
        Returns the index of time=now in the object.dates vector, or None if 'now' is not in the observed night
        """
        now = _core.E.now()
        deltadates = (self.dates[1]-self.dates[0])/2
        if now<self.dates[0]-deltadates or now>self.dates[-1]+deltadates: return None
        return (_core.np.abs(self.dates-_core.E.now())).argmin()



class Target(object):
    """
    ra in 'hh:mm:ss' or decimal degrees
    dec in 'ddd:mm:ss' or decimal degress
    """
    def __init__(self, ra, dec, name=''):
        if isinstance(ra, (float, int)):
            self._ra = _core.Angle(ra, 'deg')
        else:
            self._ra = _core.Angle(str(ra)+'h')
        self._dec = _core.Angle(str(dec)+'d')
        self.name = str(name)

    def __getitem__(self, key):
        return getattr(self, str(key).lower(), None)

    def _info(self):
        return "Target: '%s', %ih%im%2.1fs %s%i°%i'%2.1f\"" % (self.name, self._ra.hms[0], self._ra.hms[1], self._ra.hms[2], (self._dec.dms[0]>0)*'+', self._dec.dms[0], self._dec.hms[1], self._dec.hms[2])
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()


    @property
    def ra(self):
        ra = self._ra.hms
        return [int(ra[0]), int(ra[1]), ra[2]]
    @ra.setter
    def ra(self, value):
        raise AttributeError, "Read-only"

    @property
    def dec(self):
        dec = self._dec.dms
        return [int(dec[0]), int(dec[1]), dec[2]]
    @dec.setter
    def dec(self, value):
        raise AttributeError, "Read-only"

    @property
    def raStr(self):
        return "%ih%im%2.1fs" % (self._ra.hms[0], self._ra.hms[1], self._ra.hms[2])
    @property
    def decStr(self):
        return "%s%i°%i'%2.1f\"" % ((self._dec.dms[0]>0)*'+', self._dec.dms[0], self._dec.dms[1], self._dec.dms[2])

    def process(self, obs):
        save_date = obs.date # saves the date
        obs.date = obs.dates[0]
        self.airmass = []
        self.lst = []
        self.ha = []
        self.alt = []
        self.az = []
        self.moondist = []
        targetdb = "star,f|V|G2,%s,%s,0.0,2000.0" % (':'.join(map(str, self.ra)), ':'.join(map(str, self.dec)))
        target = _core.E.readdb(targetdb)
        target.compute(obs)
        self.set_time = obs.next_setting(target)
        self.set_az = _core.np.rad2deg(target.az)
        self.transit_time = obs.next_transit(target)
        if self.transit_time>self.set_time: self.transit_time = obs.previous_transit(target)
        self.transit_alt = _core.np.rad2deg(target.alt)
        self.transit_az = _core.np.rad2deg(target.az)
        obs.date = self.set_time
        self.rise_time = obs.previous_rising(target)
        self.rise_az = _core.np.rad2deg(target.az)
        for t in range(len(obs.dates)):
            obs.date = obs.dates[t] # forces the obs date for target calculation
            target.compute(obs)
            self.lst.append(obs.sidereal_time())
            self.airmass.append(_core.rad_to_airmass(target.alt))
            self.alt.append(target.alt)
            self.az.append(target.az)
            self.ha.append(self.lst[t] - target.ra)
            self.moondist.append(_core.E.separation([self.az[t], self.alt[t]], [obs.moon.az[t], obs.moon.alt[t]]))
        obs.date = save_date # sets obs date back
        self.alt = _core.np.rad2deg(self.alt)
        self.az = _core.np.rad2deg(self.az)
        self.ha = _core.np.rad2deg(self.ha)
        self.airmass = _core.np.asarray(self.airmass)
        self.moondist = _core.np.rad2deg(self.moondist)
        self.lst = _core.np.asarray(self.lst)



class Moon(Target):
    def __init__(self, obs):
        self.name = 'Moon'
        self.process(obs=obs)

    def _info(self):
        return "Moon - phase: %2.1f%%" % (self.phase.mean())
    @property
    def ra(self):
        return self._ra.hms
    @ra.setter
    def ra(self, value):
        raise AttributeError, "Read-only"

    @property
    def dec(self):
        return self._dec.dms
    @dec.setter
    def dec(self, value):
        raise AttributeError, "Read-only"

    def process(self, obs):
        save_date = obs.date # saves the date
        obs.date = _core.E.Date(obs.dates[0])
        self.lst = []
        self.ha = []
        self.airmass = []
        self.phase = []
        self.alt = []
        self.az = []
        self._ra = []
        self._dec = []
        target = _core.E.Moon()
        target.compute(obs)
        self.set_time = target.set_time#self.next_setting(target)
        self.set_az = _core.np.rad2deg(target.set_az)#_core.np.rad2deg(target.az)
        self.rise_time = target.rise_time#self.previous_rising(target)
        self.rise_az = _core.np.rad2deg(target.rise_az)#_core.np.rad2deg(target.az)
        self.transit_time = obs.next_transit(target)
        self.transit_alt = _core.np.rad2deg(target.alt)
        self.transit_az = _core.np.rad2deg(target.az)
        for t in obs.dates:
            obs.date = t # forces obs date for target calculations
            target.compute(obs) # target calculation
            self.lst.append(obs.sidereal_time())
            self.phase.append(target.phase)
            self.airmass.append(_core.rad_to_airmass(target.alt))
            self.alt.append(target.alt)
            self.az.append(target.az)
            ra, dec = obs.radec_of(self.az[-1], self.alt[-1])
            self._ra.append(ra)
            self._dec.append(dec)
            self.ha.append(self.lst[-1] - target.ra)
        obs.date = save_date # sets obs date back
        self.alt = _core.np.rad2deg(self.alt)
        self.az = _core.np.rad2deg(self.az)
        self.ha = _core.np.rad2deg(self.ha)
        self._ra = _core.Angle(self._ra, 'rad')
        self._dec = _core.Angle(self._dec, 'rad')
        self.airmass = _core.np.asarray(self.airmass)
        self.lst = _core.np.asarray(self.lst)
        self.phase = _core.np.asarray(self.phase)




class TargetSIMBAD(Target):
    """
    name as if a simbad name-search
    """
    def __init__(self, name):
        self.name = str(name)
        customSimbad = _core.Simbad()
        customSimbad.add_votable_fields('fluxdata(U)', 'fluxdata(B)', 'fluxdata(V)', 'fluxdata(R)', 'fluxdata(I)', 'fluxdata(J)', 'fluxdata(H)', 'fluxdata(K)', 'plx', 'sptype')
        result = customSimbad.query_object(str(self.name))
        self._ra = _core.Angle(str(result['RA'][0])+'h')
        self._dec = _core.Angle(str(result['DEC'][0])+'d')

        # copies the fluxes
        self.flux = {}
        if not hasattr(result['FLUX_U'][0], 'mask'): self.flux.update({'U':float(result['FLUX_U'][0])})
        if not hasattr(result['FLUX_B'][0], 'mask'): self.flux.update({'B':float(result['FLUX_B'][0])})
        if not hasattr(result['FLUX_V'][0], 'mask'): self.flux.update({'V':float(result['FLUX_V'][0])})
        if not hasattr(result['FLUX_R'][0], 'mask'): self.flux.update({'R':float(result['FLUX_R'][0])})
        if not hasattr(result['FLUX_I'][0], 'mask'): self.flux.update({'I':float(result['FLUX_I'][0])})
        if not hasattr(result['FLUX_J'][0], 'mask'): self.flux.update({'J':float(result['FLUX_J'][0])})
        if not hasattr(result['FLUX_H'][0], 'mask'): self.flux.update({'H':float(result['FLUX_H'][0])})
        if not hasattr(result['FLUX_K'][0], 'mask'): self.flux.update({'K':float(result['FLUX_K'][0])})
        self.sptype = str(result['SP_TYPE'][0])
        if not hasattr(result['PLX_VALUE'][0],'mask'):
            self.plx = float(result['PLX_VALUE'][0])
            self.dist = 1000/self.plx

        # searches for HD, HR, and HIP numbers
        for i in _core.Simbad.query_objectids(str(self.name))['ID']:
            i = i.upper()
            if i[:3]=='HD ':
                self.hd = int(_core.make_num(_core.re.sub('^(HD)','',i).strip()))
            if i[:3]=='HR ':
                self.hr = int(_core.make_num(_core.re.sub('^(HR)','',i).strip()))
            if i[:4]=='HIP ':
                self.hip = int(_core.make_num(_core.re.sub('^(HIP)','',i).strip()))

        self.link = "http://simbad.u-strasbg.fr/simbad/sim-id?Ident=" + name.replace("+","%2B").replace("#","%23").replace(" ","+")
        self.linkbib = self.link + "&submit=display&bibdisplay=refsum&bibyear1=1950&bibyear2=%24currentYear#lab_bib"


class Observation(Observatory):
    def _info(self):
        nextday = _core.E.Date(_core.E.Date(self.obsnight)+1).datetime()
        nextdaystr = [str(nextday.day)]
        if nextday.month!=self.obsnight.month: nextdaystr = [str(nextday.month)] + nextdaystr
        if nextday.year!=self.obsnight.year: nextdaystr = [str(nextday.year)] + nextdaystr
        return "Observation at %s on %i/%i/%i-%s. %i targets. Moon phase: %2.1f%%" % (self.name, self.obsnight.year, self.obsnight.month, self.obsnight.day, "/".join(nextdaystr), len(self.targets), self.moon.phase.mean())
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    @property
    def targets(self):
        if not hasattr(self, '_targets'): self._targets = []
        return self._targets
    @targets.setter
    def targets(self, value):
        if not isinstance(value, (list, tuple)): # single element
            if not isinstance(value, Target): raise AttributeError, "Can't add non-Target object to target list"
            self._targets = [value] # adds the moon and the element
            self._targets._ticked = True
        else:
            for item in value:
                if not isinstance(item, Target): raise AttributeError, "Can't add non-Target object to target list"
            self._targets = value
            for item in self._targets:
                item._ticked = True

    @property
    def ticked(self):
        if not hasattr(self, '_targets'): return []
        return [item._ticked for item in self._targets]
    @ticked.setter
    def ticked(self, value):
        raise AttributeError, "Read-only"

    def tick(self, tgt, forceTo=None):
        """
        Inverses the ticked property of the target with index tgt (int)
        Forces the tick to 'forceTo' (bool) if it is not None
        If the resulting ticked is True, reprocesses the target for the given observatory and date
        """
        if not hasattr(self, '_targets'): return None
        if isinstance(tgt, int):
            if forceTo is not None:
                self._targets[tgt]._ticked = bool(forceTo)
            else:
                self._targets[tgt]._ticked = not bool(self._targets[tgt]._ticked)
            if self._targets[tgt]._ticked is True: self._targets[tgt].process(self)
    

    def add_target(self, tgt, ra=None, dec=None, name=""):
        """
        Adds a target to the observation list
        tgt can be :
        - a Target instance,
        - a target name (then, ra and dec are its coordinates)
        - a ra-dec string (then, name is is its name)
        """
        if not hasattr(self, '_targets'): self._targets = []
        if ra is not None and dec is not None:
            self._targets += [Target(ra=ra, dec=dec, name=tgt)]
        elif isinstance(tgt, Target):
            self._targets += [tgt]
        elif isinstance(tgt, (int, float, str)): # if we have a ra-dec string
            try:
                ra, dec = _core.radecFromStr(str(tgt))
                self._targets += [Target(ra=ra, dec=dec, name=name)]
            except:
                self._targets += [TargetSIMBAD(name=tgt)]
        self._targets[-1]._ticked = True

    def rem_target(self, tgt):
        """
        Removes the target with index tgt (int) from the observation list
        """
        if not hasattr(self, '_targets'): return None
        if isinstance(tgt, int):
            self._targets.pop(tgt)
            self._ticked.pop(tgt)

    def change_obs(self, obs, long=None, lat=None, elevation=None, timezone=None, temp=None, pressure=None, moonAvoidRadius=None, horizon_obs=None, dataFile=None, recalcAll=False):
        """
        Changes the observatory and then re-processes all target for the new observatory and same date
        If recalcAll is True, all targets, even the unticked ones, are processed
        """
        targets = self._targets
        Observation.__init__(self, obs=obs, long=long, lat=lat, elevation=elevation, timezone=timezone, temp=temp, pressure=pressure, moonAvoidRadius=moonAvoidRadius, local_date=self.obsnight, horizon_obs=horizon_obs, dataFile=dataFile)
        self._targets = targets
        self.process(recalcAll=recalcAll)

    def process(self, recalcAll=False):
        """
        Processes all target for the given observatory and date
        If recalcAll is True, all targets, even the unticked ones, are processed
        """
        for item in self.targets:
            if item._ticked or recalcAll: item.process(self)
        

    def change_date(self, ut_date=None, local_date=None, recalcAll=False):
        """
        Changes the date of the observation and then re-processes all target for the same observatory and new date
        If recalcAll is True, all targets, even the unticked ones, are processed
        """
        self.upd_date(ut_date=ut_date, local_date=local_date)
        self.process(recalcAll=recalcAll)



"""
checked -> ticked
namefull -> name
az
alt
color
airmass
ha

dist
sptype
plx


"""