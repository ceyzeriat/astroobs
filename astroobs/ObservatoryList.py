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

def show_all_obs(dataFile=None, **kwargs):
    """
    A quick function to view all available observatories
    """
    dum = ObservatoryList(dataFile=dataFile, **kwargs)
    print('*'*80)
    for k, v in dum.nameList(): print(k.ljust(10)+" => "+v)
    print('*'*80)


class ObservatoryList(object):
    """
    Manages the database of observatories.

    Args:
      * dataFile (str): path+file to the observatories database. If left to ``None``, the standard package database will be used

    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      * Exception: if a mandatory input parameter is missing when loading all observatories

    Use :func:`add`, :func:`rem`, :func:`mod` to add, remove or modify an observatory to the database.
    
    >>> import astroobs.obs as obs
    >>> ol = obs.ObservatoryList()
    >>> ol
    List of 34 observatories
    >>> ol.obsids
    ['mwo',
     'kpno',
     'ctio',
     'lasilla',
     ...
     'vlt',
     'mgo',
     'ohp']
    >>> ol['ohp']
    {'elevation': 650.0,
     'lat': 0.7667376848115423,
     'long': 0.09971647793060935,
     'moonAvoidRadius': 0.25,
     'name': 'Observatoire de Haute Provence',
     'pressure': 1010.0,
     'temp': 15.0,
     'timezone': 'Europe/Paris'}
    """
    def __init__(self, dataFile=None, **kwargs):
        if dataFile is not None:
            self.dataFile = dataFile
        else:
            try:
                this_dir, this_filename = _core.os.path.split(__file__)
                self.dataFile = _core.os.path.join(this_dir, _core.obsDataFile[_core.obsDataFile.find('/')+1:])
            except:
                self.dataFile = _core.obsDataFile
        self._raiseError = bool(kwargs.get('raiseError', False))
        self._load(**kwargs)

    def _load(self, **kwargs):
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
              if _exc.raiseIt(_exc.UncompleteObservatory, self._raiseError, item[1]+" ("+item[0]+")"): return

    def _info(self):
        if not hasattr(self,'obsids'):
            if _exc.raiseIt(_exc.NonObservatoryList, self._raiseError): return
        return "List of %s observatories" % (len(self.obsids))
    def __repr__(self):
        return self._info()
    def __str__(self):
        return self._info()

    def __getitem__(self, key):
        key = str(key).lower()
        if key not in self.obsids:
            if _exc.raiseIt(_exc.UnknownObservatory, self._raiseError, key): return
        return self.obsdic[key]

    def add(self, obsid, name, long, lat, elevation, timezone, temp=15.0, pressure=1010.0, moonAvoidRadius=0.25, **kwargs):
        """
        Adds an observatory to the current observatories database.

        Args:
          * obsid (str): id of the observatory to add. Must be unique, without spaces or ;
          * name (str): name of the observatory
          * long (str - '+/-ddd:mm:ss.s'): longitude of the observatory. West is negative, East is positive
          * lat (str - '+/-dd:mm:ss.s'): latitude of the observatory. North is Positive, South is negative
          * elevation (float - m): elevation of the observatory
          * timezone (str): timezone of the observatory, as in pytz library. See note below
          * temp (float - degrees Celcius) [optional]: temperature at the observatory
          * pressure (float - hPa) [optional]: pressure at the observatory
          * moonAvoidRadius (float - degrees) [optional]: minimum distance at which a target must sit from the moon to be observed

        Kwargs:
          See :class:`ObservatoryList`

        Raises:
          * NameError: if the observatory ID already exists
          * Exception: if a mandatory input parameter is missing when reloading all observatories

        .. note::
          To view all available timezones, run:
          >>> import pytz
          >>> for tz in pytz.all_timezones:
          >>>     print(tz)
        """
        obsid = str(obsid).lower().strip()
        if obsid in self.obsids or obsid.find(' ')!=-1 or obsid.find(';')!=-1:
            if _exc.raiseIt(_exc.DuplicateObservatory, self._raiseError, obsid): return
        else:
            f = open(self.dataFile, 'a')
            newobs = '\n%s;%s;%s;%s;%4.1f;%2.1f;%4.1f;%s;%3.1f' % (obsid, str(name).replace(";",""), str(long).replace(";",""), str(lat).replace(";",""), float(elevation), float(temp), float(pressure), str(timezone).replace(";",""), float(moonAvoidRadius))
            f.write(newobs)
            f.close()
            self._load(**kwargs)

    def rem(self, obsid, **kwargs):
        """
        Removes an observatory from the current observatories database.

        Args:
          * obsid (str): id of the observatory to remove

        Kwargs:
          See :class:`ObservatoryList`

        Raises:
          * NameError: if the observatory ID does not exist
          * Exception: if a mandatory input parameter is missing when reloading all observatories
        """
        obsid = str(obsid).lower().strip()
        if obsid not in self.obsids:
            if _exc.raiseIt(_exc.UnknownObservatory, self._raiseError, obsid): return
        else:
            newlines = '\n'.join([item.strip() for item in self._wholefile if item.split(';')[0].lower()!=obsid])
            f = open(self.dataFile, 'w')
            f.writelines(newlines)
            f.close()
            self._load(**kwargs)

    def mod(self, obsid, name, long, lat, elevation, timezone, temp=15.0, pressure=1010.0, moonAvoidRadius=0.25, **kwargs):
        """
        Modifies an observatory in the current observatories database.

        Args:
          * obsid (str): id of the observatory to modify. All other parameters redefine the observatory

        Kwargs:
          See :class:`ObservatoryList`

        Raises:
          * NameError: if the observatory ID does not exist
          * Exception: if a mandatory input parameter is missing when reloading all observatories

        .. note::
          Refer to :func:`add` for details on input parameters
        """
        obsid = str(obsid).lower().strip()
        if obsid not in self.obsids:
            if _exc.raiseIt(_exc.UnknownObservatory, self._raiseError): return
        else:
            newobs = '\n%s;%s;%s;%s;%4.1f;%2.1f;%4.1f;%s;%3.1f' % (str(obsid).lower().strip(), str(name).replace(";",""), str(long).replace(";",""), str(lat).replace(";",""), float(elevation), float(temp), float(pressure), str(timezone).replace(";",""), float(moonAvoidRadius))
            newlines = '\n'.join([item.strip() for item in self._wholefile if item.split(';')[0].lower()!=str(obsid).lower()])
            newlines += newobs
            f = open(self.dataFile, 'w')
            f.writelines(newlines)
            f.close()
            self._load(**kwargs)

    def nameList(self):
        """
        Provides a list of tuples (obs id, observatory name) in the alphabetical order of the column 'observatory name'.
        """
        names = _core.np.asarray([item.split(';')[1] for item in self.lines])
        ids = _core.np.asarray([item.split(';')[0] for item in self.lines])
        namesorted = _core.np.argsort(names)
        return zip(ids[namesorted], names[namesorted])
