# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
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

 - AbstractPixOrbHardware
 - PixOrbHardware
 - PixOrbAxis
 - PixOrbAxisController
 - PixOrbShutter
 - PixOrbShutterController

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import sys
import threading

from PyQt4 import QtCore, QtGui

from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.common.loggingServices import Logger
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.plugins.abstractAxisPlugin import AbstractAxisPlugin
from papywizard.plugins.abstractStandardShutterPlugin import AbstractStandardShutterPlugin
from papywizard.plugins.abstractHardwarePlugin import AbstractHardwarePlugin
from papywizard.plugins.axisPluginController import AxisPluginController
from papywizard.plugins.hardwarePluginController import HardwarePluginController
from papywizard.plugins.standardShutterPluginController import StandardShutterPluginController
from papywizard.view.pluginFields import ComboBoxField, LineEditField, SpinBoxField, \
                                         DoubleSpinBoxField, CheckBoxField, SliderField

NAME = "PixOrb"

DEFAULT_SPEED_INDEX = 9
DEFAULT_AXIS_WITH_BREAK = False
DEFAULT_AXIS_ACCURACY = 0.1  # °

SIN11_INIT_TIMEOUT = 10.
ENCODER_FULL_CIRCLE = 1000000  # steps per turn
AXIS_TABLE = {'yawAxis': 'B',
              'pitchAxis': 'C',
              'shutter': 'B'
              }
BREAK_TABLE = {'yawAxis': 'A',
               'pitchAxis': 'C'
               }
SPEED_TABLE = { 1: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider': 160},  #  1 rev/day
                2: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider':  80},  #  2 rev/day
                3: {'initVelocity': 6000, 'accel':  5, 'decel':  5, 'slewSpeed': 38400, 'divider':  40},  #  6 rev/day
                4: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':  20},  #  1 rev/h
                5: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':  10},  #  2 rev/h
                6: {'initVelocity': 6000, 'accel': 10, 'decel': 10, 'slewSpeed': 38400, 'divider':   6},  #  5 rev/h
                7: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   5},  #  1 °/s
                8: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   4},  #  3 °/s
                9: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   3},  #  6 °/s
               10: {'initVelocity': 6000, 'accel': 80, 'decel': 80, 'slewSpeed': 38400, 'divider':   1}   # 12 °/s
               }
MANUAL_SPEED_TABLE = {'slow': 7,  # normal / 6
                      'normal': 9,
                      'fast': 10  # normal * 2
                      }


class AbstractPixOrbHardware(AbstractHardwarePlugin):
    __initSIN11 = False

    def establishConnection(self):
        """ Establish the connection.

        The SIN-11 device used to control the Pixorb axis needs to be
        initialised before any command can be sent to the axis controllers.
        """
        AbstractHardwarePlugin.establishConnection(self)
        Logger().trace("AbstractPixOrbHardware.establishConnection()")
        if not AbstractPixOrbHardware.__initSIN11:
            try:
                answer = ""
                self._driver.empty()

                # Ask the SIN-11 to scan online controllers
                self._driver.write('&')
                self._driver.setTimeout(SIN11_INIT_TIMEOUT)  # Sin-11 takes several seconds to answer
                c = ''
                while c != '\r':
                    c = self._driver.read(1)
                    if c in ('#', '?'):
                        self._driver.read(2)  # Read last CRLF
                        Logger().debug("AbstractPixOrbHardware.establishConnection(): SIN-11 '&' answer=%s" % answer)
                        raise HardwareError("Can't init SIN-11")
                    else:
                        answer += c
                answer = answer.strip()  # Remove final CRLF
                Logger().debug("AbstractPixOrbHardware.establishConnection(): SIN-11 '&' answer=%s" % answer)
                AbstractPixOrbHardware.__initSIN11 = True
                self._driver.setTimeout(ConfigManager().getFloat('Plugins/HARDWARE_COM_TIMEOUT'))
            except:
                self._connected = False
                raise


class PixOrbHardware(AbstractPixOrbHardware):
    """
    """
    def _encoderToAngle(self, codPos):
        """ Convert encoder value to degres.

        @param codPos: encoder position
        @type codPos: int

        @return: position, in °
        @rtype: float
        """
        return codPos * 360. / ENCODER_FULL_CIRCLE

    def _angleToEncoder(self, pos):
        """ Convert degres to encoder value.

        @param pos: position, in °
        @type pos: float

        @return: encoder position
        @rtype: int
        """
        return int(pos / 360. * ENCODER_FULL_CIRCLE)

    def _sendCmd(self, cmd, table=AXIS_TABLE):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @param table: controller name table to use for this command
        @type table: dict

        @return: answer
        @rtype: str
        """
        cmd = "%s%s" % (table[self.capacity], cmd)
        for nbTry in xrange(ConfigManager().getInt('Plugins/HARDWARE_COM_RETRY')):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write("%s\n" % cmd)
                c = ''
                while c != '\r':
                    c = self._driver.read(1)
                    if c in ('#', '!', '$'):
                        self._driver.read(2)  # Read last CRLF
                        raise IOError("Error on command '%s' (answer=%s)" % (cmd, answer))
                    else:
                        answer += c

            except IOError:
                Logger().exception("PixOrbHardware._sendCmd")
                Logger().warning("PixOrbHardware._sendCmd(): %s axis %s failed to send command '%s'. Retrying..." % (NAME, table[self.capacity], cmd))
            else:
                answer = answer.strip()  # Remove final CRLF
                break
        else:
            raise HardwareError("%s axis %s can't send command '%s' (answer=%s)" % (NAME, table[self.capacity], cmd, answer))
        #Logger().debug("PixOrbHardware._sendCmd(): axis %s, cmd=%s, ans=%s" % (table[self.capacity], cmd, answer))

        return answer

    def _configurePixOrb(self, speedIndex):
        """ Configure the PixOrb hardware.

        @param speedIndex: speed params table index
        @type speedIndex: int
        """
        Logger().debug("PixOrbHardware._configurePixOrb(): speedIndex=%d" % speedIndex)
        self._driver.acquireBus()
        try:

            # Set initial velocity
            self._sendCmd("I%d" % SPEED_TABLE[speedIndex]['initVelocity'])

            # Set accel/decel
            self._sendCmd("K%d %d" % (SPEED_TABLE[speedIndex]['accel'], SPEED_TABLE[speedIndex]['decel']))

            # Set slew speed
            self._sendCmd("V%d" % SPEED_TABLE[speedIndex]['slewSpeed'])

            # Set divider
            self._sendCmd("D%d" % SPEED_TABLE[speedIndex]['divider'])
        finally:
            self._driver.releaseBus()

    def _read(self):
        """ Read the axis position.

        @return: axis position, in °
        @rtype: float
        """
        self._driver.acquireBus()
        try:
            answer = self._sendCmd("Z")
        finally:
            self._driver.releaseBus()
        value = answer[1:]
        pos = self._encoderToAngle(int(value))

        # Reverse direction on yaw axis
        if self.capacity == 'yawAxis':
            pos *= -1
        #Logger().debug("PixOrbHardware._read(): pos=%d" % pos)

        return pos

    def _drive(self, pos):
        """ Drive the axis.

        @param pos: position to reach, in °
        @type pos: float
        """
        Logger().debug("PixOrbHardware._drive(): pos=%d" % pos)

        # Reverse direction on yaw axis
        if self.capacity == 'yawAxis':
            pos *= -1

        self._driver.acquireBus()
        try:
            self._sendCmd("R%+d" % self._angleToEncoder(pos))
        finally:
            self._driver.releaseBus()

    def _wait(self):
        """ Wait until motion is complete.
        """
        Logger().trace("PixOrbHardware._wait()")
        self._driver.acquireBus()
        try:
            self._sendCmd("W")
        finally:
            self._driver.releaseBus()

    def _stop(self):
        """ Stop the axis.
        """
        Logger().trace("PixOrbHardware._stop()")
        self._driver.acquireBus()
        try:
            self._sendCmd("@")
        finally:
            self._driver.releaseBus()

    def _startJog(self, dir_, speed):
        """ Start the axis.

        @param dir_: direction ('+', '-')
        @type dir_: str

        @param speed: speed
        @type speed: int
        """
        Logger().debug("PixOrbHardware._startJog(): dir_=%s, speed=%d" % (dir_, speed))
        if dir_ not in ('+', '-'):
            raise ValueError("%s axis %d dir. must be in ('+', '-')" % (NAME, AXIS_TABLE[self.capacity]))

        # Reverse direction on yaw axis
        if self.capacity == 'yawAxis':
            if dir_ == '+':
                dir_ = '-'
            else:
                dir_ = '+'

        self._driver.acquireBus()
        try:
            self._sendCmd("M%s%d" % (dir_, speed))
        finally:
            self._driver.releaseBus()

    def _releaseBreak(self):
        """ Release the (opional) break.
        """
        Logger().trace("PixOrbHardware._releaseBreak()")
        self._driver.acquireBus()
        try:
            self._sendCmd("A8", table=BREAK_TABLE)
        finally:
            self._driver.releaseBus()
        #time.sleep(.1)  # Ensure break is released

    def _activateBreak(self):
        """ Release the (opional) break.
        """
        Logger().trace("PixOrbHardware._activateBreak()")
        self._driver.acquireBus()
        try:
            self._sendCmd("A0", table=BREAK_TABLE)
        finally:
            self._driver.releaseBus()

    def _getStatus(self):
        """ Get axis status.

        @return: axis status
        @rtype: str
        """
        self._driver.acquireBus()
        try:
            answer = self._sendCmd("^")
        finally:
            self._driver.releaseBus()
        axis, status = answer.split()
        #Logger().debug("PixOrbHardware._startJog(): status=%s" % status)
        return status


class PixOrbAxis(PixOrbHardware, AbstractAxisPlugin):
    def __init__(self, *args, **kwargs):
        PixOrbHardware.__init__(self, *args, **kwargs)
        AbstractAxisPlugin.__init__(self, *args, **kwargs)

    def _init(self):
        Logger().trace("PixOrbAxis._init()")
        PixOrbHardware._init(self)
        AbstractAxisPlugin._init(self)

    def _defineConfig(self):
        AbstractAxisPlugin._defineConfig(self)
        AbstractHardwarePlugin._defineConfig(self)
        self._addConfigKey('_speedIndex', 'SPEED_INDEX', default=DEFAULT_SPEED_INDEX)
        self._addConfigKey('_axisWithBreak', 'AXIS_WITH_BREAK', default=DEFAULT_AXIS_WITH_BREAK)
        self._addConfigKey('_axisAccuracy', 'AXIS_ACCURACY', default=DEFAULT_AXIS_ACCURACY)

    def init(self):
        Logger().trace("PixOrbAxis.init()")
        AbstractAxisPlugin.init(self)
        self.configure()

    def shutdown(self):
        Logger().trace("PixOrbAxis.shutdown()")
        self.stop()
        AbstractAxisPlugin.shutdown(self)

    def configure(self):
        Logger().trace("PixOrbAxis.configure()")
        AbstractAxisPlugin.configure(self)
        self._configurePixOrb(self._config['SPEED_INDEX'])

    def read(self):
        pos = self._read()
        pos -= self._offset
        return pos

    def drive(self, pos, useOffset=True, wait=True):
        Logger().debug("PixOrbAxis.drive(): '%s' drive to %.1f" % (self.capacity, pos))
        currentPos = self.read()
        if abs(pos - currentPos) <= self._config['AXIS_ACCURACY']:
            return

        self._checkLimits(pos)

        if useOffset:
            pos += self._offset

        if self._config['AXIS_WITH_BREAK']:
            self._releaseBreak()
        self._configurePixOrb(self._config['SPEED_INDEX'])
        self._drive(pos)

        # Wait end of movement
        if wait:
            self.waitEndOfDrive()

    def waitEndOfDrive(self):
        #self._wait()
        while self.isMoving():
            time.sleep(0.1)
        self.waitStop()

    def startJog(self, dir_):
        if self._config['AXIS_WITH_BREAK']:
            self._releaseBreak()
        self._configurePixOrb(MANUAL_SPEED_TABLE[self._manualSpeed])
        self._startJog(dir_, SPEED_TABLE[MANUAL_SPEED_TABLE[self._manualSpeed]]['slewSpeed'])

    def stop(self):
        self._stop()
        self.waitStop()

    def waitStop(self):
        if self._config['AXIS_WITH_BREAK']:
            self._activateBreak()

    def isMoving(self):
        status = self._getStatus()
        if status != '0':
            return True
        else:
            return False


class PixOrbAxisController(AxisPluginController, HardwarePluginController):
    def _defineGui(self):
        AxisPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)
        self._addWidget('Main', QtGui.QApplication.translate("pixOrbPlugins", "Speed index"),
                        SpinBoxField, (1, 10, "", ""), 'SPEED_INDEX')
        self._addTab('Hard', QtGui.QApplication.translate("pixOrbPlugins", 'Hard'))
        self._addWidget('Hard', QtGui.QApplication.translate("pixOrbPlugins", "Axis with break"),
                        CheckBoxField, (), 'AXIS_WITH_BREAK')
        self._addWidget('Hard', QtGui.QApplication.translate("pixOrbPlugins", "Axis accuracy"),
                        DoubleSpinBoxField, (0.01, 0.50, 2, 0.01, "", " °"), 'AXIS_ACCURACY')


class PixOrbShutter(PixOrbHardware, AbstractStandardShutterPlugin):
    def _init(self):
        Logger().trace("PixOrbShutter._init()")
        PixOrbHardware._init(self)
        AbstractStandardShutterPlugin._init(self)

    def _defineConfig(self):
        PixOrbHardware._defineConfig(self)
        AbstractStandardShutterPlugin._defineConfig(self)

    def _triggerOnShutter(self):
        """ Set the shutter on.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("A8")
        finally:
            self._driver.releaseBus()

    def _triggerOffShutter(self):
        """ Set the shutter off.
        """
        self._driver.acquireBus()
        try:
            self._sendCmd("A0")
        finally:
            self._driver.releaseBus()

    def shutdown(self):
        Logger().trace("PixOrbShutter.shutdown()")
        self._triggerOffShutter()
        AbstractStandardShutterPlugin.shutdown(self)


class PixOrbShutterController(StandardShutterPluginController, HardwarePluginController):
    def _defineGui(self):
        StandardShutterPluginController._defineGui(self)
        HardwarePluginController._defineGui(self)


def register():
    """ Register plugins.
    """
    PluginsManager().register(PixOrbAxis, PixOrbAxisController, capacity='yawAxis', name=NAME)
    PluginsManager().register(PixOrbAxis, PixOrbAxisController, capacity='pitchAxis', name=NAME)
    PluginsManager().register(PixOrbShutter, PixOrbShutterController, capacity='shutter', name=NAME)
