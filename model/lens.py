# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

This software is governed by the B{CeCILL} license under French law and
abiding by the rules of distribution of free software.  You can  use, 
modify and/or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
U{http://www.cecill.info}.

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

Module purpose
==============

Model

Implements
==========

- Lens

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import math

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager


class Lens(object):
    """ Lens model.

    Lens orientation is landscape.
    """
    def __init__(self):
        """ Init object.
        """
    def __getFocal(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'LENS_FOCAL')
    
    def __setFocal(self, focal):
        """
        """
        ConfigManager().setFloat('Preferences', 'LENS_FOCAL', focal, 1)
        
    focal = property(__getFocal, __setFocal)
    
    def computeFov(self, size):
        """ Compute FoV.

        @param size: size of the sensor
        @type size: float

        @return: FoV of the lens
        @rtype: float
        """
        return 360. / math.pi * math.atan(size / (2. * self.focal))

    def shutdown(self):
        """ Cleanly terminate the lens

        Save values to preferences.
        """
        Logger().trace("Lens.shutdown()")
