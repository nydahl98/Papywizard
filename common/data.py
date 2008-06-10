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

Data management

Implements
==========

- Data

Usage
=====

Data is used during shooting, and generate a xml file containing
usefull information for stitchers. AutoPano Pro takes advantage of
such datas, for example to correctly set unlinked pictures at their
correct place (sky pictures without any details are often unlinked).

<?xml version="1.0" encoding="UTF-8"?>
<papywizard>
    <header>
        <focal>17.0</focal>
        <fisheye>True</fisheye>
        <sensorCoef>1.6</sensorCoef>
        <sensorRatio>3:2</sensorRatio>
        <cameraOrientation>portrait</cameraOrientation>
        <nbPicts>2</nbPicts>                             <!-- bracketing -->
        <relYawOverlap>0.54</yawRealOverlap>             <!-- real overlaps -->
        <pitchRealOverlap>0.32</pitchRealOverlap>
        <template type="mosaic" rows="3" columns="4" />
    </header>
    <shoot>
        ...
        <image id="7" pict="1">
            <time>Mon Dec 31 00:52:18 CET 2007</time>
            <yaw>-32.5</yaw>
            <pitch>12.3</pitch>
        </image>
        <image id="8" pict="2">
            <time>Mon Dec 31 00:52:22 CET 2007</time>
            <yaw>-32.5</yaw>
            <pitch>12.3</pitch>
        </image>
        ...
    </shoot>
<papywizard>

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import os.path
import xml.dom.minidom

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger


class Data(object):
    """ Manage the data.
    """
    def __init__(self):
        """ Init object.

        #@param headerInfo: informations stored in the <header> section
        #@type headerInfo: dict
        """
        Logger().debug("Data.__init__(): create xml tree")
        self.__date = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())

        # Create xml tree
        self.__impl = xml.dom.minidom.getDOMImplementation()
        self.__doc = self.__impl.createDocument(None, "papywizard", None)
        self.__rootNode = self.__doc.documentElement

        # Create 'header' node
        self.__headerNode = self.__doc.createElement('header')
        self.__rootNode.appendChild(self.__headerNode)

        # Create 'shoot' node
        self.__shootNode = self.__doc.createElement('shoot')
        self.__rootNode.appendChild(self.__shootNode)

        self.__imageId = 1

    def __createNode(self, parent, tag):
        """ Create a node.

        @param parent: parent node
        @type parent: {DOM Element}

        @param tag: name of the tag
        @type tag: str
        """
        node = self.__doc.createElement(tag)
        parent.appendChild(node)
        return node

    def __createTextNode(self, parent, tag, text):
        """ Create a text node.

        @param parent: parent node
        @type parent: {DOM Element}

        @param tag: name of the text tag
        @type tag: str

        @param text: text to use
        @type text: str
        """
        textNode = self.__createNode(parent, tag)
        text = self.__doc.createTextNode(text)
        textNode.appendChild(text)
        return textNode

    def __serialize(self):
        """ Serialize xml tree to file.
        """
        if ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE'):
            Logger().trace("Data.serialize()")
            filename = os.path.join(config.HOME_DIR, config.DATA_FILE)
            xmlFile = file(filename % self.__date, 'w')
            self.__doc.writexml(xmlFile, addindent='    ', newl='\n')
            xmlFile.close()

    def addHeaderNode(self, tag, value=None, **attr):
        """ Add a header node.

        @param tag: tag of the node
        @type tag: str

        @param value: value of the node
        @type value: str

        @param attr: optionnal attributes
        @type attr: dict
        """
        Logger().debug("Data.addHeaderNode(): tag=%s, value=%s, attr=%s" % (tag, value, attr))
        if value is not None:
            headerNode = self.__createTextNode(self.__headerNode, tag, value)
        else:
            headerNode = self.__createNode(self.__headerNode, tag)
        for key, val in attr.iteritems():
            headerNode.setAttribute(key, val)

        # Serialize xml file
        self.__serialize()

    def addImageNode(self, pict, yaw, pitch):
        """ Add a new image node to shoot node.

        @param pict: num of the pict (bracketing)
        @type pict: int

        @param yaw: yaw position
        @type yaw: float

        @param pitch: pitch position
        @type pitch: float
        """
        Logger().debug("Data.addImageNode(): pict=%d, yaw=%.1f, pitch=%.1f" % (pict, yaw, pitch))
        imageNode = self.__createNode(self.__shootNode, 'image')
        imageNode.setAttribute('id', "%d" % self.__imageId)
        self.__imageId += 1
        imageNode.setAttribute('pict', "%d" % pict)
        self.__shootNode.appendChild(imageNode)
        self.__createTextNode(imageNode, 'time', time.ctime())
        self.__createTextNode(imageNode, 'yaw', "%.1f" % yaw)
        self.__createTextNode(imageNode, 'pitch', "%.1f" % pitch)

        # Serialize xml file
        self.__serialize()
