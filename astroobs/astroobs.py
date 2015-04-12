# -*- coding: utf-8 -*-
# Written by Guillaume, 2015

import core as _core

_obsDataFile = './obsData.txt'

class ObservatoryList:
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
            print "The observatory ID provided already exists."
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
            print "The observatory ID provided was not found."
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
        if str(obsid).lower() in self.obsids:
            print "The observatory ID provided already exists."
        else:
            newobs = '\n%s;%s;%s;%s;%s;%s;%s;%s;%s' % (str(obsid).lower(), name, long, lat, elevation, temp, pressure, timezone, moonAvoidRadius)
            newlines = '\n'.join([item.strip() for item in self._wholefile if item.split(';')[0].lower()!=str(obsid).lower()])
            newlines.append(newobs)
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


class Observatory(_core.E.Observer):
    """
    Defines an observatory

    obs can be obsid or obs name if the obs is not in the database

    long: longitude in 'ddd:mm:ss.s' or decimal degrees - West is positive, East is negative
    lat: latitude in 'dd:mm:ss.s' or decimal degrees - North is Positive, South is negative
    elevation: elevation in m
    temp: temperature in celcius
    pressure: pressure in hPa
    moonAvoidRadius: radius of forbiden circle around the moon in degrees
    """
    def __init__(self, obs, long=None, lat=None, elevation=None, timezone=None, temp=15.0, pressure=1010.0, moonAvoidRadius=0, dataFile=_obsDataFile):
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
            self.temp = float(temp)
            self.pressure = float(pressure)
            self.moonAvoidRadius = float(moonAvoidRadius)
            # checks the type of long and lat
            if isinstance(long, (float, int)):
                self.long = _core.E.degrees(_core.np.deg2rad(long))
            else:
                self.long = _core.E.degrees(long)
            if isinstance(lat, (float, int)):
                self.lat = _core.E.degrees(_core.np.deg2rad(lat))
            else:
                self.lat = _core.E.degrees(lat)
        else: # a parameter is missing
            raise Exception, "One or more input parameter missing. All 'long', 'lat', 'elevation', and 'timezone' are mandatory."
        self.epoch = _core.E.J2000 # set epoch
        self.horizon = -1*_core.np.sqrt(2*self.elevation/_core.E.earth_radius)
        # initialise the date
        self.upd_date(force=True)
        self.process_obs()


    def _calc_sunRiseSet(self, mode=''):
        """
        Processes sunrise and sunset in UTC and add info to object as parameters
        mode can be: '' (horizon), 'astro' (-18 degrees), 'nautical' (-12 degrees),'civil' (-6 degrees)
        """
        degs = {'astro':'18', 'nautical':'12', 'civil':'6'}
        if mode.lower() not in degs.keys() and mode!='': raise KeyError, "Unknown twilight %s" % mode # checks for mode
        s1 = self.horizon # save initial obs values
        if mode!='': self.horizon = -1.0*_core.E.degrees(degs[mode.lower()]+':00:00.0') # set horizon from mode
        setattr(self, "sunset"+mode.lower(), self.previous_setting(_core.E.Sun())) # adds property sunset of mode
        setattr(self, "sunrise"+mode.lower(), self.next_rising(_core.E.Sun())) # adds property sunrise of mode
        if getattr(self, "sunrise"+mode.lower()) - getattr(self, "sunset"+mode.lower()) > 1: setattr(self, "sunset"+mode.lower(), self.next_setting(_core.E.Sun())) # checks issue when the date provided was during day: time between previous_setting and next_rising is longer than a day
        self.horizon = s1 # restore initial obs values



    def _process_moon(self):
        save_date = self.date # saves the date
        self.moon = Moon(name='Moon')
        self.moon.lst = []
        self.moon.ha = []
        self.moon.airmass = []
        self.moon.phase = []
        self.moon.alt = []
        self.moon.az = []
        self.date = self.dates[0]
        target = _core.E.Moon()
        target.compute(self)
        self.moon.set_time = self.next_setting(target)
        self.moon.set_az = _core.np.rad2deg(target.az)
        self.date = self.moon.set_time
        self.moon.rise_time = self.previous_rising(target)
        self.moon.rise_az = _core.np.rad2deg(target.az)
        for t in self.dates:
            self.date = t # forces obs date for target calculations
            target.compute(self) # target calculation
            self.moon.lst.append(self.sidereal_time())
            self.moon.phase.append(target.phase)
            self.moon.airmass.append(_core.rad_to_airmass(target.alt))
            self.moon.alt.append(target.alt)
            self.moon.az.append(target.az)
            self.moon.ha.append(self.moon.lst[-1] - target.ra)
        self.date = save_date # sets obs date back
        self.moon.alt = _core.np.rad2deg(self.moon.alt)
        self.moon.az = _core.np.rad2deg(self.moon.az)
        self.moon.ha = _core.np.rad2deg(self.moon.ha)
        self.moon.airmass = _core.np.asarray(self.moon.airmass)



    def upd_date(self, local_date=None, ut_date=None, force=False):
        """
        Updates the date and time to "midnight this night"
        object.obsnight gives the midnight datetime in local
        object.date gives the midnight in UT
        object.localTimeOffest gives the offset between local and UT times (negative to the West)

        force = True forces the recalculation of the date

        returns False if the date did not change since last upd_date call and True if it did
        """
        stored_date = getattr(self, 'obsnight', _core.datetime(2000, 1, 1))
        self.date = _core.E.now() # takes the now for temporary calculation
        # set the local_date to this night's sunset time in local time so we can get the local day/month/year
        self.localTimeOffest = _core.E.Date(_core.datetime.now(_core.timezone(self.timezone)))-_core.E.now()
        if local_date is None and ut_date is None: # default set to tonight midnight if date not provided
            if self.next_rising(_core.E.Sun()) - self.previous_setting(_core.E.Sun()) < 1: # if during the night
                local_date = _core.E.Date(self.previous_setting(_core.E.Sun()) + self.localTimeOffest).datetime()
            else: # if before the night
                local_date = _core.E.Date(self.next_setting(_core.E.Sun()) + self.localTimeOffest).datetime()
        elif local_date is not None: # if given local date
            _core.cleanTime(local_date)
        else: # if given ut date
            _core.cleanTime(ut_date)
        # check if the date has changed
        if stored_date.year==local_date.year and stored_date.month==local_date.month and stored_date.day==local_date.day and force is False: # didn't change
            return False
        else: # the date has changed
            self.obsnight = _core.datetime(local_date.year, local_date.month, local_date.day, 23, 59, 59) # midnight in local time
            self.date = _core.E.Date(_core.timezone(self.timezone).localize(self.obsnight).astimezone(_core.timezone('utc'))) # midnight in UT time
            return True




    def nowarg(self):
        return (_abs(self.dates-_core.E.now())).argmin()



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
        if not isinstance(self.date, _core.E.Date): raise TypeError, "Wrong date type, must be ephem.date" # checks type of date
        for mode in ['','astro','nautical','civil']: # gets sunrise and sunsets for all modes
            self._calc_sunRiseSet(mode=mode)
        self.dates = set_data_range(sunset=self.sunset, sunrise=self.sunrise, numdates=pts, margin=margin, fullhour=fullhour) # gets linearly spaced dates along the night
        self._process_moon()



class Moon:
    def __init__(self, name=''):
        self.name = name
