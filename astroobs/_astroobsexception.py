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



def raiseIt(exc, raiseoupas, *args):
    exc = exc(*args)
    if raiseoupas:
        raise(exc)
    else:
        print("\033[31m"+exc.message+"\033[39m")
        return True
    return False

class AstroobsException(Exception):
    """
    Root for astroobs Exceptions, only used to except any astroobs error, never raised
    """
    pass

class TargetMissingSIMBAD(AstroobsException):
    """
    If the target name given was not found in SIMBAD
    """
    def __init__(self, target="", *args):
        self.message = "The given object '%s' was not found in SIMBAD" % (target)
        self.args = [target] + [a for a in args]

class InputNotUnderstood(AstroobsException):
    """
    If the input was not understood
    """
    def __init__(self, ipt="", *args):
        self.message = "The input given '%s' was not understood" % (ipt)
        self.args = [ipt] + [a for a in args]

class NoPlotMode(AstroobsException):
    """
    If the user doesn't have matplotlib
    """
    def __init__(self, *args):
        self.message = "The Matplotlib library could not be imported: you are running Astroobs in NoPlot mode"
        self.args = [a for a in args]

class NonTarget(AstroobsException):
    """
    If the type of the object is not astroobs.Target, or is not valid
    """
    def __init__(self, obj="", *args):
        if str(obj)!="": obj = "'"+str(obj)+"' "
        self.message = "Object %sis not a valid Target" % (obj)
        self.args = [obj] + [a for a in args]

class ReadOnly(AstroobsException):
    """
    If the parameter is read-only
    """
    def __init__(self, attr="", *args):
        self.message = "Attribute '%s' is read-only" % (attr)
        self.args = [attr] + [a for a in args]

class UnknownTwilight(AstroobsException):
    """
    If the twilight key is not known
    """
    def __init__(self, twi="", *args):
        self.message = "Unknown twilight '%s'" % (twi)
        self.args = [twi] + [a for a in args]

class UnknownObservatory(AstroobsException):
    """
    If the observatory key is not known
    """
    def __init__(self, obs="", *args):
        self.message = "Unknown observatory '%s'" % (obs)
        self.args = [obs] + [a for a in args]

class DuplicateObservatory(AstroobsException):
    """
    If the observatory key is already existing
    """
    def __init__(self, key="", *args):
        self.message = "Observatory key already exists '%s'" % (key)
        self.args = [key] + [a for a in args]

class UncompleteObservatory(AstroobsException):
    """
    If one or more parameter is missing in the setting up of the Obervatory object
    """
    def __init__(self, param="", *args):
        self.message = "Parameter '%s' is mandatory to create the observatory" % (param)
        self.args = [param] + [a for a in args]

class NonObservatory(AstroobsException):
    """
    If one or more parameter is missing in the setting up of the Obervatory object
    """
    def __init__(self, obs="", *args):
        if str(obs)!="": obs = "'"+str(obs)+"' "
        self.message = "Object %sis not a valid Observatory." % (obs)
        self.args = [obs] + [a for a in args]

class NoObservatoryDate(UncompleteObservatory):
    """
    If the observatory is missing a date
    """
    def __init__(self, *args):
        self.message = "No date associated to the observatory"
        self.args = [a for a in args]

class NonObservatoryList(AstroobsException):
    """
    If the observatory list is not valid
    """
    def __init__(self, *args):
        self.message = "Object is not a valid Observatory List"
        self.args = [a for a in args]

