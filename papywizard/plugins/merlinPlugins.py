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

Hardware

Implements
==========

- MerlinHardware
- MerlinAxis
- MerlinAxisController
- MerlinYawAxis
- MerlinYawAxisController
- MerlinPitchAxis
- MerlinPitchAxisController
- MerlinShutter
- MerlinShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.common import config
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.common.pluginManager import PluginManager
from papywizard.common.helpers import decodeAxisValue, encodeAxisValue, deg2cod, cod2deg
from papywizard.hardware.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.hardware.abstractShutterPlugin import AbstractShutterPlugin
from papywizard.hardware.hardwarePlugin import HardwarePlugin
from papywizard.controller.axisPluginController import AxisPluginController
from papywizard.controller.hardwarePluginController import HardwarePluginController
from papywizard.controller.shutterPluginController import ShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, DoubleSpinBoxField, CheckBoxField, SliderField


class MerlinHardware:
    name = "Merlin"

    def _init(self):
        self._numAxis = None

    def _sendCmd(self, cmd, param=""):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str
        """
        cmd = "%s%d%s" % (cmd, self._numAxis, param)
        for nbTry in xrange(3):
            try:
                answer = ""
                self._driver.acquireBus()
                try:
                    self._driver.empty()
                    #self._driver.setCS(0)
                    self._driver.write(":%s\r" % cmd)
                    c = ''
                    while c not in ('=', '!'):
                        c = self._driver.read(1)
                    if c == '!':
                        c = self._driver.read(1) # Get error code
                        raise IOError("Merlin didn't understand the command (err=%d)" % c)
                    answer = ""
                    while True:
                        c = self._driver.read(1)
                        if c == '\r':
                            break
                        answer += c

                finally:
                    #self._driver.setCS(1)
                    self._driver.releaseBus()

            except IOError:
                Logger().exception("MerlinHardware._sendCmd")
                Logger().warning("MerlinHardware._sendCmd(): axis %d can't sent command. Retrying..." % self._numAxis)
            else:
                break
        else:
            raise HardwareError("Merlin axis %d can't send command" % self._numAxis)
        #Logger().debug("MerlinHardware._sendCmd(): axis %d cmd=%s, ans=%s" % (self._numAxis, cmd, answer))

        return answer


class MerlinAxis(MerlinHardware, AbstractAxisPlugin, HardwarePlugin):
    def _init(self):
        MerlinHardware._init(self)
        AbstractAxisPlugin._init(self)
        self._manualSpeed = config.MANUAL_SPEED['normal']

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        HardwarePlugin._defineConfig(self)

    def activate(self):
        Logger().trace("MerlinHardware.activate()")

    def shutdown(self):
        Logger().trace("MerlinHardware.shutdown()")

    def establishConnection(self):
        HardwarePlugin.establishConnection(self)
        self._driver.acquireBus()
        try:

            # Stop axis
            self._sendCmd("L")

            # Check motor?
            self._sendCmd("F")

            # Get full circle count
            value = self._sendCmd("a")
            Logger().debug("MerlinAxis.establishConnection(): full circle count=%s" % hex(decodeAxisValue(value)))

            # Get
            value = self._sendCmd("D")
            Logger().debug("MerlinAxis.establishConnection(): sidereal rate=%s" % hex(decodeAxisValue(value)))
        finally:
            self._driver.releaseBus()

    def shutdownConnection(self):
        self.stop()
        HardwarePlugin.shutdownConnection(self)

    def read(self):
        self._driver.acquireBus()
        try:
            value = self._sendCmd("j")
        finally:
            self._driver.releaseBus()
        pos = cod2deg(decodeAxisValue(value))
        pos -= self._offset

        return pos

    def drive(self, pos, inc=False, useOffset=True, wait=True):
        currentPos = self.read()

        # Compute absolute position from increment if needed
        if inc:
            pos = currentPos + inc
        else:
            if useOffset:
                pos += self._offset

        self._checkLimits(pos)

        # Choose between default (hardware) method or external closed-loop method
        # Not yet implemented (need to use a thread; see below)
        if pos - currentPos < 6.:
            #self._driveWithExternalClosedLoo(pos)
            self._driveWithInternalClosedLoop(pos)
        else:
            self._driveWithInternalClosedLoop(pos)

        # Wait end of movement
        # Does not work for external closed-loop drive. Need to execute drive in a thread.
        if wait:
            self.waitEndOfDrive()

    def _driveWithInternalClosedLoop(self, pos):
        """ Default (hardware) drive.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().trace("Axis._drive1()")
        strValue = encodeAxisValue(deg2cod(pos))
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            self._sendCmd("G", "00")
            self._sendCmd("S", strValue)
            #self._sendCmd("I", encodeAxisValue(self._manualSpeed))
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()

    #def _driveWithExternalClosedLoop(self, pos):
        #""" External closed-loop drive.

        #This method implements an external closed-loop regulation.
        #It is faster for angles < 6-7°, because in this case, the
        #head does not accelerate to full speed, but rather stays at
        #very low speed.

        #Problem: this drive can't be stopped, neither run concurrently
        #on both axis without big modifications in multi-threading stuff.

        #@param pos: position to reach, in °
        #@type pos: float
        #"""
        #Logger().trace("Axis._driveWithExternalClosedLoop()")
        #self._driver.acquireBus()
        #try:
            #self._sendCmd("L")
            #initialPos = self.read()

            ## Compute direction
            #if pos > initialPos:
                #self._sendCmd("G", "30")
            #else:
                #self._sendCmd("G", "31")

            ## Load speed
            #self._sendCmd("I", "500000") # Use manual speed

            ## Start move
            #self._sendCmd("J")
        #finally:
            #self._driver.releaseBus()

        ## Closed-loop drive
        #stopRequest = False
        #while abs(pos - self.read()) > .5: # optimal delta depends on speed/inertia

            ## Test if a stop request has been sent
            #if not self.isMoving():
                #break
            #time.sleep(0.1)
        #self.stop()

        ## Final drive (auto) if needed
        #if abs(pos - self.read()) > config.AXIS_ACCURACY and not stopRequest:
            #self._drive1(pos)

    def stop(self):
        self._sendCmd("L")
        self.waitStop()

    def waitEndOfDrive(self):
        while True:
            if not self.isMoving():
                break
            time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        self._driver.acquireBus()
        try:
            self._sendCmd("L")
            if dir_ == '+':
                self._sendCmd("G", "30")
            elif dir_ == '-':
                self._sendCmd("G", "31")
            else:
                raise ValueError("Axis %d dir. must be in ('+', '-')" % self._numAxis)

            self._sendCmd("I", encodeAxisValue(self._manualSpeed))
            self._sendCmd("J")
        finally:
            self._driver.releaseBus()

    def waitStop(self):
        pos = self.read()
        time.sleep(0.05)
        while True:
            if round(abs(pos - self.read()), 1) == 0:
                break
            pos = self.read()
            time.sleep(0.05)

    def _getStatus(self):
        return self._sendCmd("f")

    def isMoving(self):
        status = self._getStatus()
        if status[1] != '0':
            return True
        else:
            return False

    def setOutput(self, level):
        self._driver.acquireBus()
        try:
            if level:
                self._sendCmd("O", "1")
            else:
                self._sendCmd("O", "0")
        finally:
            self._driver.releaseBus()

    def setManualSpeed(self, speed):
        self._manualSpeed = config.MANUAL_SPEED[speed]


class MerlinAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


class MerlinYawAxis(MerlinAxis):
    capacity = 'yawAxis'

    def _init(self):
        MerlinAxis._init(self)
        self._numAxis = 1


class MerlinYawAxisController(MerlinAxisController):
    pass


class MerlinPitchAxis(MerlinAxis):
    capacity = 'pitchAxis'

    def _init(self):
        MerlinAxis._init(self)
        self._numAxis = 2


class MerlinPitchAxisController(MerlinAxisController):
    pass


class MerlinShutter(MerlinHardware, AbstractShutterPlugin, HardwarePlugin):
    def _getTimeValue(self):
        return self._config["TIME_VALUE"]

    def _getMirrorLockup(self):
        return self._config["MIRROR_LOCKUP"]

    def _getBracketingNbPicts(self):
        return self._config["BRACKETING_NB_PICTS"]

    def _getBracketingIntent(self):
        return self._config["BRACKETING_INTENT"]

    def _init(self):
        self._numAxis = 1 # shutter contact is connected on axis 1 µ-controller

    def _defineConfig(self):
        AbstractShutterPlugin._defineConfig(self)
        HardwarePlugin._defineConfig(self)
        self._addConfigKey('_timeValue', 'TIME_VALUE', default=0.5)
        self._addConfigKey('_mirrorLockup', 'MIRROR_LOCKUP', default=False)
        self._addConfigKey('_bracketingNbPicts', 'BRACKETING_NB_PICTS', default=1)
        self._addConfigKey('_bracketingIntent', 'BRACKETING_INTENT', default='exposure')
        self._addConfigKey('_pulseWidthHigh', 'PULSE_WIDTH_HIGH', default=100)
        self._addConfigKey('_pulseWidthLow', 'PULSE_WIDTH_LOW', default=100)

    def activate(self):
        pass

    def shutdown(self):
        pass

    def lockupMirror(self):
        Logger().trace("MerlinShutter.lockupMirror()")
        self._driver.acquireBus()
        try:
            self._sendCmd("O", "1")
            time.sleep(self.config['PULSE_WIDTH_HIGH'] / 1000.)
            self._sendCmd("O", "0")
            return 0
        finally:
            self._driver.releaseBus()

    def shoot(self):
        # TODO: ensure PULSE_WIDTH_LOW delay
        Logger().trace("MerlinShutter.shoot()")
        self._driver.acquireBus()
        try:
            self._sendCmd("O", "1")
            time.sleep(self.config['PULSE_WIDTH_HIGH'] / 1000.)
            self._sendCmd("O", "0")
            return 0
        finally:
            self._driver.releaseBus()


class MerlinShutterController(ShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        ShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', "Time value", DoubleSpinBoxField, (0.1, 3600, 1, "", " s"), 'TIME_VALUE')
        self._addWidget('Main', "Mirror lockup", CheckBoxField, (), 'MIRROR_LOCKUP')
        self._addWidget('Main', "Bracketing nb picts", SpinBoxField, (1, 99), 'BRACKETING_NB_PICTS')
        self._addWidget('Main', "Bracketing intent", ComboBoxField, (['exposure', 'focus', 'white balance', 'movement'],), 'BRACKETING_INTENT')
        self._addWidget('Main', "Pulse width high", SpinBoxField, (10, 1000, "", " ms"), 'PULSE_WIDTH_HIGH')
        self._addWidget('Main', "Pulse width low", SpinBoxField, (10, 1000, "", " ms"), 'PULSE_WIDTH_LOW')


def register():
    """ Register plugins.
    """
    PluginManager().register(MerlinYawAxis, MerlinYawAxisController)
    PluginManager().register(MerlinPitchAxis, MerlinPitchAxisController)
    PluginManager().register(MerlinShutter, MerlinShutterController)
