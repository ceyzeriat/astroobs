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

from .Target import Target

class TargetSIMBAD(Target):
    """
    Initialises a target object from an online SIMBAD database name-search. Optionaly, processes the target for the observatory and date given (refer to :func:`TargetSIMBAD.process`).

    Args:
      * name (str): the name of the target as if performing an online SIMBAD search
      * obs (:class:`Observatory`) [optional]: the observatory for which to process the target
    
    Kwargs:
      * raiseError (bool): if ``True``, errors will be raised; if ``False``, they will be printed. Default is ``False``

    Raises:
      N/A

    Creates attributes:
      * ``flux``: a dictionary of the magnitudes of the target. Keys are part or all of ['U','B','V','R','I','J','H','K']
      * ``link``: the link to paste into a web-browser to display the SIMBAD page of the target
      * ``linkbib``: the link to paste into a web-browser to display the references on the SIMBAD page of the target
      * ``hd``: if applicable, the HD number of the target
      * ``hr``: if applicable, the HR number of the target
      * ``hip``: if applicable, the HIP number of the target
    """
    def __init__(self, name, obs=None, input_epoch='2000', **kwargs):
        self._raiseError = bool(kwargs.get('raiseError', False))
        self.name = str(name)
        self.input_epoch = str(int(input_epoch))
        customSimbad = _core.Simbad()
        customSimbad.add_votable_fields('fluxdata(U)', 'fluxdata(B)', 'fluxdata(V)', 'fluxdata(R)', 'fluxdata(I)', 'fluxdata(J)', 'fluxdata(H)', 'fluxdata(K)', 'plx', 'sptype')
        self._error = False
        try:
            result = customSimbad.query_object(self.name)
        except:
            self._error = True
        if self._error is True or result is None:
            self._error = True
            if _exc.raiseIt(_exc.TargetMissingSIMBAD, self._raiseError, self.name): return
        self._ra = _core.Angle(str(result['RA'][0])+'h')
        self._dec = _core.Angle(str(result['DEC'][0])+'d')

        # copies the fluxes
        self.flux = {}
        if not hasattr(result['FLUX_U'][0], 'mask'): self.flux['U'] = float(result['FLUX_U'][0])
        if not hasattr(result['FLUX_B'][0], 'mask'): self.flux['B'] = float(result['FLUX_B'][0])
        if not hasattr(result['FLUX_V'][0], 'mask'): self.flux['V'] = float(result['FLUX_V'][0])
        if not hasattr(result['FLUX_R'][0], 'mask'): self.flux['R'] = float(result['FLUX_R'][0])
        if not hasattr(result['FLUX_I'][0], 'mask'): self.flux['I'] = float(result['FLUX_I'][0])
        if not hasattr(result['FLUX_J'][0], 'mask'): self.flux['J'] = float(result['FLUX_J'][0])
        if not hasattr(result['FLUX_H'][0], 'mask'): self.flux['H'] = float(result['FLUX_H'][0])
        if not hasattr(result['FLUX_K'][0], 'mask'): self.flux['K'] = float(result['FLUX_K'][0])
        self.sptype = str(result['SP_TYPE'][0])
        if not hasattr(result['PLX_VALUE'][0],'mask'):
            self.plx = float(result['PLX_VALUE'][0])
            self.dist = 1000/self.plx

        # searches for HD, HR, and HIP numbers
        for i in _core.Simbad.query_objectids(self.name)['ID']:
            i = i.upper()
            if i[:3]=='HD ':
                self.hd = int(_core.make_num(_core.re.sub('^(HD)','',i).strip()))
            if i[:3]=='HR ':
                self.hr = int(_core.make_num(_core.re.sub('^(HR)','',i).strip()))
            if i[:4]=='HIP ':
                self.hip = int(_core.make_num(_core.re.sub('^(HIP)','',i).strip()))

        self.link = "http://simbad.u-strasbg.fr/simbad/sim-id?Ident=" + self.name.replace("+","%2B").replace("#","%23").replace(" ","+")
        self.linkbib = self.link + "&submit=display&bibdisplay=refsum&bibyear1=1950&bibyear2=%24currentYear#lab_bib"
        if obs is not None: self.process(obs=obs, **kwargs)
