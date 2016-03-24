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

