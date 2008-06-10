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

Configuration

Implements
==========

- ConfigManager

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import os.path
import sets
import ConfigParser

from papywizard.common import config


class ConfigManager(object):
    """ ConfigManager.
    """
    __state = {}
    __init = True

    def __new__(cls, *args, **kwds):
        """ Implement the Borg pattern.
        """
        self = object.__new__(cls, *args, **kwds)
        self.__dict__ = cls.__state
        return self

    def __init__(self):
        """ Init the object.
        
        @todo: update user config. from global config. instead of overwriting
        """
        if ConfigManager.__init:
            
            # Load global config.
            globalConfig = ConfigParser.SafeConfigParser()
            if globalConfig.read(config.GLOBAL_CONFIG_FILE) == []:
                if globalConfig.read(config.CONFIG_FILE) == []:
                    raise IOError("Can't read configuration file")
            globalConfigVersion = globalConfig.getint('General', 'CONFIG_VERSION')
            
            # Check if user config. exists
            userConfig = ConfigParser.SafeConfigParser()
            if userConfig.read(config.USER_CONFIG_FILE) == []:
                print "User config. does not exist; copying from global config."
                globalConfig.write(file(config.USER_CONFIG_FILE, 'w'))
                userConfig.read(config.USER_CONFIG_FILE)

            # Check if user config. needs to be updated
            elif globalConfigVersion > userConfig.getint('General', 'CONFIG_VERSION'):
                print "User config. has wrong version.; updating from global config."
                
                # Remove obsolete sections
                globalSections = globalConfig.sections()
                for userSection in userConfig.sections():
                    if userSection not in globalSections:
                        userConfig.remove_section(userSection)
                        print "Removed [%s] section" % userSection

                # Update all sections
                for globalSection in globalSections:

                    # Create new sections
                    if not userConfig.has_section(globalSection):
                        userConfig.add_section(globalSection)
                        print "Added [%s] section" % globalSection

                    # Remove obsolete options
                    for option in userConfig.options(globalSection):
                        if not globalConfig.has_option(globalSection, option):
                            userConfig.remove_option(globalSection, option)
                            print "Removed [%s] %s option" % (globalSection, option)

                    # Update the options
                    for option, value in globalConfig.items(globalSection):
                        if not userConfig.has_option(globalSection, option) or \
                           value != userConfig.get(globalSection, option) and not globalSection.endswith("Preferences"):
                            userConfig.set(globalSection, option, value)
                            print "Updated [%s] %s option with %s" % (globalSection, option, value)
                        
                    # Set config. version
                    userConfig.set('General', 'CONFIG_VERSION', "%d" % globalConfigVersion)
                
                # Write user config.
                userConfig.write(file(config.USER_CONFIG_FILE, 'w'))
                print "User config. written to file"
                
            self.__config = userConfig

            ConfigManager.__init = False

    def save(self):
        """ Save config.
        
        Config is saved in user directory. Preferences are first
        set back to config.
        """
        self.__config.write(file(config.USER_CONFIG_FILE, 'w'))

    def get(self, section, option):
        """ Get a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to get value from
        @type option: str
        """
        return self.__config.get(section, option)

    def getInt(self, section, option):
        """ Get a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to get value from
        @type option: int
        """
        return self.__config.getint(section, option)

    def getFloat(self, section, option):
        """ Get a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to get value from
        @type option: float
        """
        return self.__config.getfloat(section, option)

    def getBoolean(self, section, option):
        """ Get a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to get value from
        @type option: bool
        """
        return self.__config.getboolean(section, option)
        
    def set(self, section, option, value):
        """ Set a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to set value to
        @type option: str
        
        @param value: value to set
        @type value: str
        """
        self.__config.set(section, option, value)
        
    def setInt(self, section, option, value):
        """ Set a value as int.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to set value to
        @type option: str
        
        @param value: value to set
        @type value: int
        """
        self.__config.set(section, option, "%d" % value)
        
    def setFloat(self, section, option, value, prec):
        """ Set a value as float.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to set value to
        @type option: str
        
        @param value: value to set
        @type value: float
        
        @param prec: precision
        @type prec: int
        """
        self.__config.set(section, option, ("%(format)s" % {'format': "%%.%df" % prec}) % value)
        
    def setBoolean(self, section, option, value):
        """ Set a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to set value to
        @type option: str
        
        @param value: value to set
        @type value: str
        """
        self.__config.set(section, option, str(value))
        