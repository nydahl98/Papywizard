#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

Main script

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import threading

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.qLoggingFormatter import QSpaceColorFormatter
from papywizard.plugins.pluginsManager  import PluginsManager
from papywizard.view.logBuffer import LogBuffer


class BlackHole:
    """ Dummy class for stderr redirection.
    """
    softspace = 0

    def write(self, text):
        pass


def main():
    try:
        # Give a name to the main trhead
        threading.currentThread().setName("Main")

        # Init the logger
        if hasattr(sys, "frozen"):

            # Forbid all console outputs
            sys.stderr = BlackHole()
            Logger(defaultStreamHandler=False)
        else:
            Logger()

        # Create the buffer for GUI log
        logStream = LogBuffer()
        Logger().addStreamHandler(logStream, QSpaceColorFormatter)

        Logger().info("Starting Papywizard...")

        # Misc infos
        Logger().debug("main(): platform=%s" % config.platform)

        # Init global Qt application
        qtApp = QtGui.QApplication(sys.argv)
        qtApp.setApplicationName("Papywizard")
        qtApp.setApplicationVersion(config.VERSION)

        # Create the splashscreen
        from papywizard.common import pixmaps
        pixmap = QtGui.QPixmap()
        pixmap.load(":/pixmaps/%s" % config.SPLASHCREEN_FILE)
        splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
        splash.show()
        qtApp.processEvents()

        # Addtional imports
        Logger().info("Importing modules...")
        splash.showMessage("Importing modules...")
        qtApp.processEvents()
        from papywizard.common import i18n
        from papywizard.common.configManager import ConfigManager
        #from papywizard.common.publisher import Publisher
        from papywizard.model.shooting import Shooting
        from papywizard.controller.mainController import MainController
        from papywizard.controller.spy import Spy
        from papywizard.view import icons

        # i18n stuff
        Logger().info("Loading i18n files...")
        splash.showMessage("Loading i18n files...")
        qtApp.processEvents()
        locale = QtCore.QLocale.system().name()
        Logger().debug("main(): locale=%s" % locale)
        qtTranslator = QtCore.QTranslator()
        if qtTranslator.load("qt_%s" % locale,
                             QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)):
            qtApp.installTranslator(qtTranslator)
        else:
            Logger().warning("Can't find qt translation file")
        appTranslator = QtCore.QTranslator()
        if appTranslator.load("papywizard_%s" % locale, ":/i18n"):
            qtApp.installTranslator(appTranslator)
        else:
            Logger().warning("Can't find papywizard translation file")

        # Load Qt stylesheet
        Logger().info("Loading Style Sheets...")
        splash.showMessage("Loading Style Sheets...")
        qtApp.processEvents()
        try:
            styleSheet = file(config.USER_STYLESHEET_FILE)
            qtApp.setStyleSheet(styleSheet.read())
            styleSheet.close()
        except IOError:
            Logger().warning("No user Style Sheet found")
        styleSheet = qtApp.styleSheet()
        if styleSheet:
            if styleSheet.startsWith("file://"):
                Logger().debug("Style Sheet loaded from command line param.")
            else:
                Logger().debug("User Style Sheet loaded")

        # Load user configuration
        Logger().info("Loading configuration...")
        splash.showMessage("Loading configuration...")
        qtApp.processEvents()
        ConfigManager().load()

        # Load plugins (move to shooting?)
        Logger().info("Load plugins...")
        splash.showMessage("Load plugins...")
        from papywizard.plugins.dslrRemoteProPlugins import register
        register()
        from papywizard.plugins.eosUtilityPlugins import register
        register()
        from papywizard.plugins.genericTetheredPlugins import register
        register()
        from papywizard.plugins.gigaPanBotPlugins import register
        register()
        from papywizard.plugins.gphotoBracketPlugins import register
        register()
        from papywizard.plugins.merlinOrionPlugins import register
        register()
        from papywizard.plugins.nkRemotePlugins import register
        register()
        from papywizard.plugins.panoduinoPlugins import register
        register()
        from papywizard.plugins.pixOrbPlugins import register
        register()
        from papywizard.plugins.simulationPlugins import register
        register()
        from papywizard.plugins.timelordPlugins import register
        register()
        from papywizard.plugins.ursaMinorBt2Plugins import register
        register()
        from papywizard.plugins.ursaMinorUsbPlugins import register
        register()
        from papywizard.plugins.claussPlugins import register
        register()
        from papywizard.plugins.owlPlugins import register
        register()
        PluginsManager ().load()

        # Activate selected plugins (move to PluginsManager ?)
        Logger().info("Activate plugins...")
        plugin = ConfigManager().get('Plugins/PLUGIN_YAW_AXIS')
        PluginsManager ().get('yawAxis', plugin)[0].activate()
        plugin = ConfigManager().get('Plugins/PLUGIN_PITCH_AXIS')
        PluginsManager ().get('pitchAxis', plugin)[0].activate()
        plugin = ConfigManager().get('Plugins/PLUGIN_SHUTTER')
        PluginsManager ().get('shutter', plugin)[0].activate()

        # Create model
        Logger().info("Creating model...")
        splash.showMessage("Creating model...")
        qtApp.processEvents()
        model = Shooting()

        # Create spy thread
        Logger().info("Starting Spy...")
        Spy(model).start()

        # Create main controller
        Logger().info("Creating GUI...")
        splash.showMessage("Creating GUI...")
        qtApp.processEvents()
        mainController = MainController(model, logStream)

        # Set user logger level
        Logger().setLevel(ConfigManager().get('Configuration/LOGGER_LEVEL'))

        # Terminate splashscreen
        splash.finish(mainController._view)

        # Check if teh configuration is set
        if not ConfigManager().isConfigured():
            from papywizard.view.messageDialog import InfoMessageDialog
            #dialog = WarningMessageDialog(QtCore.QObject().tr("Configuration"),
                                          #QtCore.QObject().tr("Papywizard needs to be configured"))
            dialog = InfoMessageDialog(QtGui.QApplication.translate("main", "Plugins selection"),
                                       QtGui.QApplication.translate("main", "Before you can use Papywizard, you must choose what " \
                                                                    "plugins to use to control your hardware.\n\n" \
                                                                    "After closing this dialog, you will be prompt to select " \
                                                                    "these plugins. Once it is done, you can configure them "
                                                                    "in the global Configuration dialog"))
            dialog.exec_()
            from papywizard.controller.pluginsController import PluginsController
            controller = PluginsController(None, model)
            controller.exec_()
            controller.shutdown()

        # Enter Qt main loop
        qtApp.exec_()

        # Shutdown controller
        Logger().info("Shuting down GUI...")
        mainController.shutdown()

        # Stop spy thread
        Logger().info("Shuting down Spy...")
        Spy().stop()
        Logger().debug("Waiting Spy thread to terminate...")
        Spy().wait()

        # Shutdown model
        Logger().info("Shuting down model...")
        model.shutdown()

        # Cleanup resources
        Logger().info("Cleaning up resources...")
        i18n.qCleanupResources()
        pixmaps.qCleanupResources()
        icons.qCleanupResources()

        Logger().info("Papywizard stopped")

    except Exception, msg:
        Logger().exception("main()")
        if 'splash' in locals():
            splash.finish(None)
        from papywizard.view.messageDialog import ExceptionMessageDialog
        try:
            msg = msg.message # Windows exception?
        except AttributeError:
            pass
        dialog = ExceptionMessageDialog("Unhandled exception", unicode(msg))
        dialog.exec_()


if __name__ == "__main__":
    sys.argv[0] = "Papywizard"
    main()
