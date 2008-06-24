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

View

Implements
==========

- ManualMoveDialog

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import os
import sys

#import pygtk
#pygtk.require("2.0")
import gtk.glade
import pango

path = os.path.dirname(__file__)


class ManualMoveDialog(object):
    """ Manual move dialog.
    """
    def __init__(self):
        """ Init the object.
        """
        # Set the Glade file
        gladeFile = os.path.join(path, "manualMoveDialog.glade")
        self.wTree = gtk.glade.XML(gladeFile)

        # Retreive usefull widgets
        self._retreiveWidgets()
        
        # Font test
        self.yawPosLabel.modify_font(pango.FontDescription("Arial 10 Bold"))
        self.pitchPosLabel.modify_font(pango.FontDescription("Arial 10 Bold"))

    def _retreiveWidgets(self):
        """ Get widgets from widget tree.
        """
        self.manualMoveDialog = self.wTree.get_widget("manualMoveDialog")
        self.yawPosLabel = self.wTree.get_widget("yawPosLabel")
        self.pitchPosLabel = self.wTree.get_widget("pitchPosLabel")
        self.setStartButton = self.wTree.get_widget("setStartButton")
        self.setEndButton = self.wTree.get_widget("setEndButton")
        self.yawMovePlusButton = self.wTree.get_widget("yawMovePlusButton")
        self.pitchMovePlusButton = self.wTree.get_widget("pitchMovePlusButton")
        self.pitchMoveMinusButton = self.wTree.get_widget("pitchMoveMinusButton")
        self.yawMinusButton = self.wTree.get_widget("yawMinusButton")

    def fillWidgets(self, values):
        """ Fill widgets with values.
        """
        self.yawPosLabel.set_text("%.1f" % values['yawPos'])
        self.pitchPosLabel.set_text("%.1f" % values['pitchPos'])
