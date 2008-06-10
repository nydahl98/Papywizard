# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Configuration.

Implements class:

- ConfigManager

@author: Fr�d�ric Mantegazza
@copyright: 2008
@license: CeCILL
@todo: 
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
                        if not userConfig.has_option(globalSection, option) or value != userConfig.get(globalSection, option):
                            if option.upper() in ('LOGGER_FORMAT', 'DATA_FILE'):
                                value = value.replace('%', '%%')
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
        