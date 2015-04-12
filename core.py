# -*- coding: utf-8 -*-
# Written by Guillaume, 2015

import ephem as E
import numpy as np
from pytz import timezone
from datetime import datetime
from time import struct_time


def cleanTime(t, format=None):
    """
    Raises an error if t not among (ephem.Date, datetime, timestamp, tuple, time.struct_time) date type, and optionaly returns the date into the format:
    - 'ts': unix timestamp (float)
    - 'dt': datetime
    - 'du': date tuple
    - 'ed': ephem.Date
    - 'st': time.struct_time

    ND: does not keep the tzinfo of datetime
    """
    if format is None: return t
    if isinstance(t, E.Date):
        pass
    elif isinstance(t, float):
        t = E.Date(datetime.fromtimestamp(t))
    elif isinstance(t, (tuple, struct_time)):
        t = E.Date(tuple(t)[:6])
    elif isinstance(t, datetime):
        t = E.Date(t)
    else:
        raise TypeError, "Wrong date format, must be ephem.Date, datetime, timestamp (float), tuple, or time.struct_time"
    format = str(format).lower()
    if format=='ts': return time.mktime(t.datetime().timetuple())
    if format=='dt': return t.datetime()
    if format=='tu': return t.tuple()
    if format=='ed': return t
    if format=='st': return t.datetime().timetuple()
    raise KeyError, "Unknown date format: %s" % str(format)

def convertTime(t, tzTo, tzFrom='utc', format=None):
    """
    Converts the time 't' from timezone 'tzFrom' (default is UT) to timezone 'tzTo'.

    tzFrom and tzTo are like 'America/Los_Angeles'

    CF cleanTime method to see possible types for 't' and output.
    """
    if format is None:
        if isinstance(t, E.Date):
            format = 'ed'
        elif isinstance(t, float):
            format = 'ts'
        elif isinstance(t, datetime):
            format = 'dt'
        elif isinstance(t, struct_time):
            format = 'st'
        elif isinstance(t, tuple):
            format = 'tu'
        else:
            format = 'ed'
    t = cleanTime(t, format='dt')
    t = timezone(tzFrom).localize(t).astimezone(timezone(tzTo))
    return cleanTime(t, format=format)


def airmass_to_rad(x):
    """
    Transforms airmass to radians
    """
    if np.size(x)>1: x = np.asarray(x)
    return np.arcsin(np.true_divide(1, x))


def rad_to_airmass(x):
    """
    Transforms radians to airmass
    """
    if np.size(x)>1:
        x = np.asarray(x).copy()
        if (x<0.05).any(): x[x<0.05] = 0.05
    else:
        if x<0.05: x=0.05
    sz = np.true_divide(1, np.sin(x)) - 1.0
    return 1.0 + sz*(0.9981833 - sz*(0.002875 + sz*0.0008083))
