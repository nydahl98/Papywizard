# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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

Plugin

Implements
==========

-  AbstractStandardShutterPlugin

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time

from papywizard.common.loggingServices import Logger
from papywizard.hardware.abstractShutterPlugin import AbstractShutterPlugin
DEFAULT_TIME_VALUE = 0.5 # s
DEFAULT_MIRROR_LOCKUP = False
DEFAULT_BRACKETING_NBPICTS = 1
DEFAULT_BRACKETING_INTENT = 'exposure'
DEFAULT_PULSE_WIDTH_HIGH = 200 # ms
DEFAULT_PULSE_WIDTH_LOW = 200 # ms


class  AbstractStandardShutterPlugin(AbstractShutterPlugin):
    def _init(self):
        Logger().trace("AbstractStandardShutterPlugin._init()")
        AbstractShutterPlugin._init(self)
        self.__LastShootTime = time.time()

    def _getTimeValue(self):
        return self._config["TIME_VALUE"]

    def _getMirrorLockup(self):
        return self._config["MIRROR_LOCKUP"]

    def _getBracketingNbPicts(self):
        return self._config["BRACKETING_NB_PICTS"]

    def _getBracketingIntent(self):
        return self._config["BRACKETING_INTENT"]

    def _defineConfig(self):
        self._addConfigKey('_timeValue', 'TIME_VALUE', default=DEFAULT_TIME_VALUE)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=DEFAULT_MIRROR_LOCKUP)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=DEFAULT_BRACKETING_NBPICTS)
        self._addConfigKey('_bracketingIntent', 'BRACKETING_INTENT', default=DEFAULT_BRACKETING_INTENT)
        self._addConfigKey('_pulseWidthHigh', 'PULSE_WIDTH_HIGH', default=DEFAULT_PULSE_WIDTH_HIGH)
        self._addConfigKey('_pulseWidthLow', 'PULSE_WIDTH_LOW', default=DEFAULT_PULSE_WIDTH_LOW)

    def _ensurePulseWidthLowDelay(self):
        """ Ensure that PULSE_WIDTH_LOW delay has elapsed before last trigger.
        """
        delay = self._config['PULSE_WIDTH_LOW'] / 1000. - (time.time() - self.__LastShootTime)
        if delay > 0:
            time.sleep(delay)