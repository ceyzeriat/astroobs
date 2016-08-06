# -*- coding: utf-8 -*-
# 
# Copyright ASTROOBS (c) 2015-20016 Guillaume SCHWORER
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

import ephem as E
import numpy as np
from pytz import timezone
from datetime import datetime
from time import struct_time, mktime
from astropy.coordinates.angles import Angle
from astroquery.simbad import Simbad
import re
import os
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    NOPLOT = False
except:
    NOPLOT = True
# force UTF-8 for python 2.x
from sys import version_info
if version_info[0] < 3:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

obsDataFile = './obsData.txt'
many_color = ['#40AC1E','#4E9FCC','#9A4ECC','#CC7B4E','#4E2ECC','#CC9EBD','#8EDCCD','#DC1ED2','#F21616','#2816F2','#3BF216','#F2E016']

def radecFromStr(txt):
    """
    Takes a string that contains ra in decimal degrees or in hh:mm:ss.s and dec in decimal degrees or dd:mm:ss.s
    returns (ra, dec) in decimal degrees
    """
    def check_str(text, rem_char=None):
        if not isinstance(rem_char, str): raise Exception("rem_char argument must be a string")
        reps = {}
        for elmt in rem_char:
            reps.update({elmt:""})
        text = replace_multi(text, reps)
        return text
    def replace_multi(text, reps):
        """
        Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern in string by the replacement repl.
        """
        rep = dict((re.escape(k).lower(), v) for k, v in reps.iteritems())
        pattern = re.compile("|".join(rep.keys()), re.IGNORECASE)
        return pattern.sub(lambda m: rep[re.escape(m.group(0)).lower()], text)
    deli = check_str(txt, rem_char="+-.,0123456789abcdefghijklmnopqrstuvwxyz")
    if len(deli)==1:
        ra, dec = txt.split(deli)
    elif len(deli)<5:
        raise ValueError("Could not understand ra-dec formating")
    elif len(deli)==5 or (deli[0]==deli[1] and deli[3]==deli[4]):
        ra = txt[:txt.find(deli[2], txt.find(deli[0], txt.find(deli[0]) +1) +1)].strip()
        txt = txt.replace(ra,"")
        dec = txt[txt.find(deli[2])+1:].strip()
    else:
        raise ValueError("Could not understand ra-dec formating")
    try:
        ra = E.degrees(float(ra)) # test si decmal degrees
    except:
        try:
            ra = Angle(ra+'h').deg # hourangle
        except:
            raise ValueError("Could not understand ra-dec formating")
    try:
        dec = E.degrees(dec) # decimal degrees or hms
    except:
        raise ValueError("Could not understand ra-dec formating")
    return ra, dec

def make_num(numstr):
    """
    Removes any non-number character from numstr. Keeps also decimal separator "." and signs "-", "+".
    Returns float
    """
    decimal = re.compile(r'[^\d.\-\+]+').sub('', numstr)
    # there might still be one or several + or - in the middle of the string, or several dots
    return float(re.compile(r'^[\+\-]?[0-9]*\.?[0-9]*').match(decimal).group())

def cleanTime(t, format=None):
    """
    Raises an error if t not among (ephem.Date, datetime, timestamp, tuple, time.struct_time) date types, and optionaly returns the date into the format:
    - 'ts': unix timestamp (float)
    - 'dt': datetime
    - 'du': date tuple
    - 'ed': ephem.Date
    - 'st': time.struct_time

    NB: does not keep the tzinfo of datetime
    """
    tinit = t
    if isinstance(t, E.Date):
        pass
    elif isinstance(t, float):
        t = E.Date(datetime.fromtimestamp(t))
    elif isinstance(t, (tuple, struct_time)):
        t = E.Date(tuple(t)[:6])
    elif isinstance(t, datetime):
        t = E.Date(t)
    else:
        raise TypeError("Wrong date format, must be ephem.Date, datetime, timestamp (float), tuple, or time.struct_time")
    if format is None: return tinit
    format = str(format).lower()
    if format=='ts': return mktime(t.datetime().timetuple())
    if format=='dt': return t.datetime()
    if format=='tu': return t.tuple()
    if format=='ed': return t
    if format=='st': return t.datetime().timetuple()
    raise KeyError("Unknown date format: %s" % str(format))

def convertTime(t, tzTo, tzFrom='utc', format=None):
    """
    Converts the time 't' from timezone 'tzFrom' (default is UT) to timezone 'tzTo'.

    tzFrom and tzTo are like 'America/Los_Angeles'

    cf cleanTime method to see possible types for 't' and output.
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


def airmass_to_rad(arr):
    """
    Transforms airmass to radians
    """
    if np.size(arr)>1: arr = np.asarray(arr)
    return np.arcsin(np.true_divide(1, arr))


def rad_to_airmass(arr):
    """
    Transforms radians to airmass
    """
    if np.size(arr)>1:
        arr = np.asarray(x).copy()
        if (arr<0.05).any(): arr[arr<0.05] = 0.05
    else:
        if arr<0.05: arr = 0.05
    sz = np.true_divide(1, np.sin(arr)) - 1.0
    return 1.0 + sz*(0.9981833 - sz*(0.002875 + sz*0.0008083))
