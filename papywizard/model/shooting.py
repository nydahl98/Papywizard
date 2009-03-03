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

Model

Implements
==========

- Shooting

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import imp

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.helpers import hmsAsStrToS, sToHmsAsStr
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.common.exception import HardwareError
from papywizard.model.camera import Camera
from papywizard.model.data import MosaicData, PresetData
from papywizard.model.scan import MosaicScan, PresetScan

# Try to import the 'shoot' module from user config. dir
try:
    file, pathname, description = imp.find_module("shoot", [config.USER_CONFIG_DIR])
    try:
        externalShooting = imp.load_module('externalShooting', file, pathname, description)
    finally:
        file.close()
except ImportError:
    Logger().exception("Shooting.start(): loading user external shooting script", debug=True)
    Logger().warning("No user external shooting script found")


class Shooting(QtCore.QObject):
    """ Shooting model.
    """
    def __init__(self, realHardware, simulatedHardware, parent=None):
        """ Init the object.

        @param realHardware: real hardware head
        @type realHardware: {Head}

        @param simulatedHardware: simulated hardware head
        @type simulatedHardware: {HeadSimulation}
        """
        QtCore.QObject.__init__(self, parent)
        self.__shooting = False
        self.__pause = False
        self.__paused = False
        self.__stop = False
        self.__stepByStep = False
        self.__forceNewPosition = False
        self.__startTime = None
        self.__pauseTime = None
        self.__totalPausedTime = 0.
        self.__LastShootTime = time.time()
        # Hardware
        self.realHardware = realHardware
        self.simulatedHardware = simulatedHardware
        self.hardware = self.simulatedHardware

        # Sub-models
        self.camera = Camera()
        self.mosaic = MosaicScan(self)
        self.preset = PresetScan(self)

    # Properties
    def __getMode(self):
        return ConfigManager().get('Main', 'SHOOTING_MODE')

    def __setMode(self, mode):
        ConfigManager().set('Main', 'SHOOTING_MODE', mode)

    mode = property(__getMode, __setMode)

    def __getStabilizationDelay(self):
        return ConfigManager().getFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY')

    def __setStabilizationDelay(self, stabilizationDelay):
        ConfigManager().setFloat('Preferences', 'SHOOTING_STABILIZATION_DELAY', stabilizationDelay, 1)

    stabilizationDelay = property(__getStabilizationDelay, __setStabilizationDelay)

    def __getHeadOrientation(self):
        """
        """
        return ConfigManager().get('Preferences', 'SHOOTING_HEAD_ORIENTATION')

    def __setHeadOrientation(self, headOrientation):
        """
        """
        ConfigManager().set('Preferences', 'SHOOTING_HEAD_ORIENTATION', headOrientation)

    headOrientation = property(__getHeadOrientation, __setHeadOrientation)

    def __getCameraOrientation(self):
        """
        """
        return ConfigManager().get('Preferences', 'SHOOTING_CAMERA_ORIENTATION')

    def __setCameraOrientation(self, cameraOrientation):
        """
        """
        ConfigManager().set('Preferences', 'SHOOTING_CAMERA_ORIENTATION', cameraOrientation)

    cameraOrientation = property(__getCameraOrientation, __setCameraOrientation)

    def __getCameraRoll(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'SHOOTING_CAMERA_ROLL')

    def __setCameraRoll(self, cameraRoll):
        """
        """
        ConfigManager().setFloat('Preferences', 'SHOOTING_CAMERA_ROLL', cameraRoll, 1)

    cameraRoll = property(__getCameraRoll, __setCameraRoll)

    def __getTimerAfter(self):
        """
        """
        return hmsAsStrToS(ConfigManager().get('Preferences', 'TIMER_AFTER'))

    def __setTimerAfter(self, s):
        """
        """
        ConfigManager().set('Preferences', 'TIMER_AFTER', sToHmsAsStr(s))

    timerAfter = property(__getTimerAfter, __setTimerAfter)

    def __getTimerAfterEnable(self):
        """
        """
        return ConfigManager().getBoolean('Preferences', 'TIMER_AFTER_ENABLE')

    def __setTimerAfterEnable(self, flag):
        """
        """
        ConfigManager().setBoolean('Preferences', 'TIMER_AFTER_ENABLE', flag)

    timerAfterEnable = property(__getTimerAfterEnable, __setTimerAfterEnable)

    def __getTimerRepeat(self):
        """
        """
        return ConfigManager().getInt('Preferences', 'TIMER_REPEAT')

    def __setTimerRepeat(self, repeat):
        """
        """
        ConfigManager().setInt('Preferences', 'TIMER_REPEAT', repeat)

    timerRepeat = property(__getTimerRepeat, __setTimerRepeat)

    def __getTimerRepeatEnable(self):
        """
        """
        return ConfigManager().getBoolean('Preferences', 'TIMER_REPEAT_ENABLE')

    def __setTimerRepeatEnable(self, flag):
        """
        """
        ConfigManager().setBoolean('Preferences', 'TIMER_REPEAT_ENABLE', flag)

    timerRepeatEnable = property(__getTimerRepeatEnable, __setTimerRepeatEnable)

    def __getTimerEvery(self):
        """
        """
        return hmsAsStrToS(ConfigManager().get('Preferences', 'TIMER_EVERY'))

    def __setTimerEvery(self, s):
        """
        """
        ConfigManager().set('Preferences', 'TIMER_EVERY', sToHmsAsStr(s))

    timerEvery = property(__getTimerEvery, __setTimerEvery)

    def __getScan(self):
        """
        """
        if self.mode == 'mosaic':
            return self.mosaic
        else:
            return self.preset

    scan = property(__getScan)

    # Signals
    def hardwareConnected(self, flag, message=""):
        """ Hardware connect/disconnect.

        @param flag: True if connected, false otherwise
        @type flag: bool

        @param message: optional error message
        @type message: str
        """
        self.emit(QtCore.SIGNAL("hardwareConnected"), flag, message)

    def started(self):
        """ Shooting started.
        """
        self.emit(QtCore.SIGNAL("started"))

    def paused(self):
        """ Shooting paused.
        """
        self.emit(QtCore.SIGNAL("paused"))

    def resumed(self):
        """ Shooting resumed.
        """
        self.emit(QtCore.SIGNAL("resumed"))

    def stopped(self, status):
        """ Shooting stopped.

        @param status: shooting status
        @type status: str
        """
        self.emit(QtCore.SIGNAL("stopped"), status)

    def waiting(self, wait):
        """ Shooting waiting.

        @param wait: remaining time to wait (s)
        @type wait: float
        """
        self.emit(QtCore.SIGNAL("waiting"), wait)

    def progress(self, shootingProgress=None, totalProgress=None):
        """ Shooting progress.

        @param shootingProgress: shooting progress value
        @type shootingProgress: float

        @param totalProgress: total progress value
        @type totalProgress: float
        """
        self.emit(QtCore.SIGNAL("progress"), shootingProgress, totalProgress)

    def repeat(self, repeat):
        """ Shooting repeat counter.

        @param repeat: repeat counter
        @type repeat: int
        """
        self.emit(QtCore.SIGNAL("repeat"), repeat)

    def update(self, index, yaw, pitch, state=None, next=None):
        """ Shooting update.

        @param index: position index
        @type int

        @param yaw: position yaw
        @type yaw: float

        @param pitch: position pitch
        @type pitch: float

        @param state: position state
        @type state: str

        @param next: next position flag
        @type next: bool
        """
        self.emit(QtCore.SIGNAL("update"), index, yaw, pitch, state, next)

    def sequence(self, sequence, bracket=None):
        """ Shooting sequence.

        @param sequence: name of the current sequence
        @type sequence: str

        @param bracket: number of the bracket
        @type bracket: int
        """
        self.emit(QtCore.SIGNAL("sequence"), sequence, bracket)

    # Interface
    def setStartEndFromFov(self, yawFov, pitchFov):
        """ Set yaw start/end positions from total fov.

        @param yawFov: total yaw fov (°)
        @type yawFov: float

        @param pitchFov: total pitch fov (°)
        @type pitchFov: float
        """
        yawPos, pitchPos = 0., 0.
        yawDelta = yawFov - self.camera.getYawFov(self.cameraOrientation)
        if yawDelta < 0.:
            yawDelta = 0.
        self.mosaic.yawStart = yawPos - yawDelta / 2.
        self.mosaic.yawEnd = yawPos + yawDelta / 2.
        pitchDelta = pitchFov - self.camera.getPitchFov(self.cameraOrientation)
        if pitchDelta < 0.:
            pitchDelta = 0.
        self.mosaic.pitchStart = pitchPos - pitchDelta / 2.
        self.mosaic.pitchEnd = pitchPos + pitchDelta / 2.

    def setStartEndFromNbPicts(self, yawNbPicts, pitchNbPicts):
        """ Set the start/end positions from nb picts.

        @param yawNbPicts: yaw nb picts
        @type yawNbPicts: int

        @param pitchNbPicts: pitch nb picts
        @type pitchNbPicts: int
        """
        yawPos, pitchPos = 0., 0.
        yawDelta = self.camera.getYawFov(self.cameraOrientation) * (1 - self.mosaic.overlap) * (yawNbPicts - 1)
        if yawNbPicts > 1:
            yawDelta -= .01
        self.mosaic.yawStart = yawPos - yawDelta / 2.
        self.mosaic.yawEnd = yawPos + yawDelta / 2.
        pitchDelta = self.camera.getPitchFov(self.cameraOrientation) * (1 - self.mosaic.overlap) * (pitchNbPicts - 1)
        if pitchNbPicts > 1:
            pitchDelta -= .01
        self.mosaic.pitchStart = pitchPos - pitchDelta / 2.
        self.mosaic.pitchEnd = pitchPos + pitchDelta / 2.

    def switchToRealHardware(self):
        """ Use real hardware.
        """
        Logger().trace("Shooting.switchToRealHardware()")
        try:
            #self.simulatedHardware.shutdown()
            self.realHardware.init()
            Logger().debug("Shooting.switchToRealHardware(): realHardware initialized")
            self.hardware = self.realHardware
            self.hardwareConnected(True)
        except HardwareError, message:
            Logger().exception("Shooting.switchToRealHardware()")
            self.hardwareConnected(False, str(message))

    def switchToSimulatedHardware(self):
        """ Use simulated hardware.
        """
        Logger().trace("Shooting.switchToSimulatedHardware()")
        try:
            self.realHardware.shutdown() # Test if init first
        except:
            Logger().exception("Shooting.switchToSimulatedHardware()")
        self.hardware = self.simulatedHardware
        self.hardware.init()

    def setStepByStep(self, flag):
        """ Turn on/off step-by-step shooting.

        If active, the head switch to pause at each end of position.

        @param flag: flag for step-by-step shooting
        @type flag: bool
        """
        self.__stepByStep = flag

    def forceNewPosition(self):
        self.__forceNewPosition = True

    def getShootingElapsedTime(self):
        """ Get the shooting elapsed time.

        @return: shooting time and elapsed time (s)
        @rtype: tuple of int
        """
        shootingTime = time.time() - self.__startTime - self.__totalPausedTime
        if self.__paused and self.__pauseTime is not None:
            shootingTime -= time.time() - self.__pauseTime
        elapsedTime = time.time() - self.__startTime
        return shootingTime, elapsedTime

    def start(self):
        """ Start pano shooting.
        """
        def checkPause():
            """ Check if pause requested.
            """
            if self.__pause:
                Logger().info("Pause shooting")
                self.__pauseTime = time.time()
                self.__paused = True
                self.paused()
                while self.__pause:
                    time.sleep(0.1)
                self.__paused = False
                self.resumed()
                self.__totalPausedTime += time.time() - self.__pauseTime
                Logger().info("Resume shooting")

        def checkStop():
            """ Check if stop requested.
            """
            if self.__stop:
                Logger().info("Stop shooting")
                raise StopIteration

        Logger().trace("Shooting.start()")
        self.__startTime = time.time()
        self.__totalPausedTime = 0.
        self.__stop = False
        self.__pause = False
        self.__paused = False
        self.__shooting = True
        self.started()
        self.progress(0., 0.)

        if self.cameraOrientation == 'portrait':
            roll = 90.
        elif self.cameraOrientation == 'landscape':
            roll = 0.
        elif self.cameraOrientation == 'custom':
            roll = self.cameraRoll
        else:
            raise ValueError("cameraOrientation must be in ('portrait', 'landscape', 'custom'")
        values = {'title' : ConfigManager().get('Preferences', 'DATA_TITLE'),
                  'gps': ConfigManager().get('Preferences', 'DATA_GPS'),
                  'comment': ConfigManager().get('Preferences', 'DATA_COMMENT') % {'version': config.VERSION},
                  'headOrientation': "up",
                  'cameraOrientation': "%s" % self.cameraOrientation,
                  'roll': "%.1f" % roll,
                  'stabilizationDelay': "%.1f" % self.stabilizationDelay,
                  'timeValue': "%.1f" % self.camera.timeValue,
                  'bracketingNbPicts': "%d" % self.camera.bracketingNbPicts,
                  'bracketingIntent': "%s" % self.camera.bracketingIntent,
                  'sensorCoef': "%.1f" % self.camera.sensorCoef,
                  'sensorRatio': "%s" % self.camera.sensorRatio,
                  'lensType': "%s" % self.camera.lens.type_,
                  'focal': "%.1f" % (self.camera.lens.focal * self.camera.lens.opticalMultiplier)}

        Logger().info("Start shooting process...")
        try:

            # Timer after
            if self.timerAfterEnable:
                initialTime = time.time()
                remainingTime = self.timerAfter - (time.time() - initialTime)
                while remainingTime > 0:
                    Logger().debug("Shooting.start(): start in %s" % sToHmsAsStr(remainingTime))
                    self.waiting(remainingTime)
                    time.sleep(1)

                    # Check only stop
                    checkStop()

                    remainingTime = self.timerAfter - (time.time() - initialTime)

            # Timer repeat
            if self.timerRepeatEnable:
                numRepeat =  self.timerRepeat
            else:
                numRepeat = 1
            for repeat in xrange(1, numRepeat + 1):

                # Create data object
                if self.mode == 'mosaic':
                    Logger().debug("Shooting.start(): create mosaic data object")
                    data = MosaicData()
                    values.update({'yawNbPicts': "%d" % self.mosaic.yawNbPicts,
                                   'pitchNbPicts': "%d" % self.mosaic.pitchNbPicts,
                                   'overlap': "%.2f" % self.mosaic.overlap,
                                   'yawRealOverlap': "%.2f" % self.mosaic.yawRealOverlap,
                                   'pitchRealOverlap': "%.2f" % self.mosaic.pitchRealOverlap})
                else:
                    Logger().debug("Shooting.start(): create preset data object")
                    data = PresetData()
                    values.update({'name': "%s" % self.preset.name})
                data.createHeader(values)

                startTime = time.time()
                Logger().debug("Shooting.start(): repeat %d/%d" % (repeat, numRepeat))
                self.repeat(repeat)
                self.progress(0.)

                # Loop over all positions
                self.scan.index = 1
                while True:
                    try:
                        index, (yaw, pitch) = self.scan.getCurrentPosition()
                        if isinstance(index, tuple):
                            index_, yawIndex, pitchIndex = index
                        else:
                            index_ = index
                        Logger().debug("Shooting.start(): position index=%s, yaw=%.1f, pitch=%.1f" % (str(index), yaw, pitch))
                        self.update(index, yaw, pitch, next=True)

                        self.__forceNewPosition = False

                        Logger().info("Moving")
                        self.sequence('moving')
                        self.hardware.gotoPosition(yaw, pitch)

                        # Test step-by-step flag (use a function)
                        if self.__stepByStep and not self.__stop:
                            self.__pause = True
                            Logger().info("Wait for manual shooting trigger...")

                        checkPause()
                        checkStop()

                        # If a new shooting position has been requested (rewind/forward),
                        # we start over
                        if self.__forceNewPosition:
                            continue

                        # Take pictures
                        for bracket in xrange(1, self.camera.bracketingNbPicts + 1):

                            # Mirror lockup sequence
                            if self.camera.mirrorLockup:
                                Logger().info("Mirror lockup")
                                self.sequence('mirror')
                                try:
                                    retCode, stdout, stderr = externalShooting.mirrorLockup()
                                    Logger().debug("Shooting.start(): externalShooting.mirrorLockup() return code=%d" % retCode)
                                    if stderr:
                                        Logger().debug("Shooting.start(): externalShooting.mirrorLockup() stderr:\n%s" % stderr)
                                    Logger().debug("Shooting.start(): externalShooting.mirrorLockup() stdout:\n%s" % stdout)
                                except (NameError, AttributeError):
                                    Logger().exception("Shooting.start()", debug=True)
                                    self.hardware.shoot(self.camera.pulseWidthHigh / 1000.)
                                except:
                                    Logger().exception("Shooting.start()")
                                    raise HardwareError("External shooting script failed on 'mirrorLockup()'")
                                if retCode:
                                    raise HardwareError("External shooting script failed on 'mirrorLockup()'")

                            Logger().info("Stabilization")
                            self.sequence('stabilization')
                            time.sleep(self.stabilizationDelay)

                            # Take pictures
                            Logger().info("Shutter cycle")
                            Logger().debug("Shooting.start(): pict #%d of %d" % (bracket, self.scan.totalNbPicts))
                            self.sequence('shutter', bracket)

                            # Ensure that pulse width low delay has elapsed before last shoot
                            delay = self.camera.pulseWidthLow / 1000. - (time.time() - self.__LastShootTime)
                            if delay > 0:
                                time.sleep(delay)
                            try:
                                retCode, stdout, stderr = externalShooting.shoot(bracket)
                                Logger().debug("Shooting.start(): externalShooting.shoot() return code=%d" % retCode)
                                if stderr:
                                    Logger().debug("Shooting.start(): externalShooting.shoot() stderr:\n%s" % stderr)
                                Logger().debug("Shooting.start(): externalShooting.shoot() stdout:\n%s" % stdout)
                            except (NameError, AttributeError):
                                Logger().exception("Shooting.start()", debug=True)
                                self.hardware.shoot(self.camera.pulseWidthHigh / 1000.)
                            except:
                                Logger().exception("Shooting.start()")
                                raise HardwareError("External shooting script failed on 'shoot()'")
                            if retCode:
                                raise HardwareError("External shooting script failed on 'shoot()'")
                            self.__LastShootTime = time.time()

                            # Wait for the end of shutter cycle
                            if self.camera.timeValue - self.camera.pulseWidthHigh / 1000. > 0:
                                time.sleep(self.camera.timeValue - self.camera.pulseWidthHigh / 1000.)

                            # Add image to the xml data file
                            data.addPicture(bracket, yaw, pitch, roll)

                            checkStop()

                    except HardwareError:
                        self.hardware.stopAxis()
                        Logger().exception("Shooting.start()")
                        Logger().warning("Shooting.start(): position index=%s, yaw=%.1f, pitch=%.1f out of limits" % (index_, yaw, pitch))
                        state = 'error'

                    else:
                        state = 'ok'

                    # Update global shooting progression
                    shootingProgress = float(index_) / float(self.scan.totalNbPicts)
                    totalProgress = (repeat - 1) * self.scan.totalNbPicts + index_
                    totalProgress /= float(numRepeat * self.scan.totalNbPicts)
                    self.progress(shootingProgress, totalProgress)
                    self.update(index, yaw, pitch, state=state)

                    # Next position
                    end = False
                    try:
                        self.scan.index += 1
                    except IndexError:

                        # Force index behond valid position. Hugly!!!
                        # Better find a way to tell the view not to display the next position
                        self.scan.setOverPosition()
                        self.update(self.scan.index, yaw, pitch, next=True)
                        end = True
                    else:
                        index, (yaw, pitch) = self.scan.getCurrentPosition()
                        if isinstance(index, tuple):
                            index_, yawIndex, pitchIndex = index
                        else:
                            index_ = index
                        Logger().debug("Shooting.start(): position index=%s, yaw=%.1f, pitch=%.1f" % (str(index), yaw, pitch))
                        self.update(index, yaw, pitch, next=True)


                    # Test manual shooting flag
                    # skipped if timeValue is 0
                    if self.camera.timeValue and self.__stepByStep and not self.__stop:
                        self.__pause = True
                        Logger().info("Wait for manual shooting trigger...")

                    checkPause()
                    checkStop()

                    # If a new shooting position has been requested (rewind/forward),
                    # we start over
                    if self.__forceNewPosition:
                        continue

                    # If the sequence is finished, we leave the loop
                    if end:
                        break

                if repeat < numRepeat:
                    remainingTime = self.timerEvery - (time.time() - startTime)
                    while remainingTime > 0:
                        Logger().debug("Shooting.start(): restart in %s" % sToHmsAsStr(remainingTime))
                        self.waiting(remainingTime)
                        time.sleep(1)
                        remainingTime = self.timerEvery - (time.time() - startTime)

                        checkStop()

        except StopIteration:
            Logger().debug("Shooting.start(): stop detected")
            status = 'cancel'
            Logger().warning("Shoot process canceled")
        except:
            Logger().exception("Shooting.start()")
            status = 'fail'
            Logger().error("Shoot process failed")
        else:
            status = 'ok'
            Logger().info("Shoot process finished")

        self.__shooting = False
        self.stopped(status)

    def isShooting(self):
        """ Test if shooting is running.

        @return: True if shooting is running, False otherwise
        @rtype: bool
        """
        return self.__shooting

    def pause(self):
        """ Pause execution of pano shooting.
        """
        Logger().trace("Shooting.pause()")
        self.__pause = True

    def isPaused(self):
        """ Test if shotting is paused.

        @return: True if shooting is paused, False otherwise
        @rtype: bool
        """
        return self.__paused

    def resume(self):
        """ Resume  execution of shooting.
        """
        Logger().trace("Shooting.resume()")
        self.__pause = False

    def stop(self):
        """ Cancel execution of shooting.
        """
        Logger().trace("Shooting.stop()")
        self.__stop = True
        self.__pause = False
        self.hardware.stopAxis()

    def shutdown(self):
        """ Cleanly terminate the model.

        Save values to preferences.
        """
        Logger().trace("Shooting.shutdown()")
        self.hardware.shutdown()
        self.camera.shutdown()
        ConfigManager().save()
