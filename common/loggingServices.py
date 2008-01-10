# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

misc classes.

Implements class:

- DefaultFormatter
- ColorFormatter
- Logger

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import logging
import logging.handlers
import StringIO
import traceback

from common import config


consoleLogColors = {'trace':"\033[0;36;40;22m",     # cyan/noir, normal
                    'debug':"\033[0;36;40;1m",      # cyan/noir, gras
                    'info':"\033[0;37;40;1m",       # blanc/noir, gras
                    'warning':"\033[0;33;40;1m",    # marron/noir, gras
                    'error':"\033[0;31;40;1m",      # rouge/noir, gras
                    'exception':"\033[0;35;40;1m",  # magenta/noir, gras
                    'critical':"\033[0;37;41;1m",   # blanc/rouge, gras
                    'default':"\033[0m",            # defaut
                    }


class DefaultFormatter(logging.Formatter):
    """ Base class for formatters.
    """


class ColorFormatter(DefaultFormatter):
    """ Color formatting.
    
    This formatter add colors to the log, according to their level.
    
    @todo: do not use colors for windows...
    """
    def _colorFormat(self, record):
        if record.levelname == 'TRACE':
            color = consoleLogColors['trace']
        elif  record.levelname == 'DEBUG':
            color = consoleLogColors['debug']
        elif  record.levelname == 'INFO':
            color = consoleLogColors['info']
        elif  record.levelname == 'WARNING':
            color = consoleLogColors['warning']
        elif record.levelname == 'ERROR':
            color = consoleLogColors['error']
        elif record.levelname == 'EXCEPTION':
            color = consoleLogColors['exception']
        elif record.levelname == 'CRITICAL':
            color = consoleLogColors['critical']
        else:
            color = consoleLogColors['default']
        formattedMsg = DefaultFormatter.format(self, record)
        return color + formattedMsg + consoleLogColors['default']
        
    def format(self, record):
        """ Record formating.
        """
        return self._colorFormat(record)


class Logger(object):
    """ Logger object.

    Logger is a Borg.
    """
    __state = {}
    __init = True

    def __new__(cls, *args, **kwds):
        """ Create the object.
        """
        self = object.__new__(cls, *args, **kwds)
        self.__dict__ = cls.__state
        return self
        
    def __init__(self):
        """ Init object.
        """
        if Logger.__init:
            logging.TRACE = logging.DEBUG - 5
            logging.EXCEPTION = logging.DEBUG + 5
            #logging.EXCEPTION = logging.ERROR + 5
            logging.raiseExceptions = 0
            logging.addLevelName(logging.TRACE, "TRACE")
            logging.addLevelName(logging.EXCEPTION, "EXCEPTION")
            
            # Formatters
            colorFormatter = ColorFormatter(config.LOGGER_FORMAT)
            defaultFormatter = DefaultFormatter(config.LOGGER_FORMAT)
            
            # Handlers
            if config.LOGGER_CONSOLE:
                self.__streamHandler = logging.StreamHandler()
                self.__streamHandler.setLevel(logging.TRACE)
                self.__streamHandler.setFormatter(colorFormatter)
            
            if config.LOGGER_FILE:
                self.__fileHandler = logging.handlers.RotatingFileHandler(config.LOGGER_FILENAME,
                                                                          maxBytes=config.LOGGER_MAXBYTES,
                                                                          backupCount=config.LOGGER_BACKUPCOUNT)
                self.__fileHandler.setLevel(logging.TRACE)
                self.__fileHandler.setFormatter(defaultFormatter)

            # Loggers
            self.__logger = logging.getLogger('panohead')
            self.__logger.setLevel(logging.TRACE)
            if config.LOGGER_CONSOLE:
                self.__logger.addHandler(self.__streamHandler)
            if config.LOGGER_FILE:
                self.__logger.addHandler(self.__fileHandler)
            
            Logger.__init = False

    def __setLevel(self, handler, level):
        """ Change logging level.
        
        @param handler: handler to change level ('console', 'file')
        @type handler: str
        
        @param level: new level, in ('trace', 'debug', 'info', 'warning', 'error', 'exception', 'critical')
        @type level: str
        """
        if level not in ('trace', 'debug', 'info', 'warning', 'error', 'exception', 'critical'):
            raise ValueError("Logger level must be in ('trace', 'debug', 'info', 'warning', 'error', 'exception', 'critical')")
        levels = {'trace': logging.TRACE,
                  'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'exception': logging.EXCEPTION,
                  'critical': logging.CRITICAL}
        handler.setLevel(levels[level])

    def setConsoleLevel(self, level):
        """ Change logging level for console output.
        
        @param level: new level
        @type level: str
        """
        self.__setLevel(self.__streamHandler, level)

    def setFileLevel(self, level):
        """ Change logging level for file output.
        
        @param level: new level
        @type level: str
        """
        self.__setLevel(self.__fileHandler, level)
        
    def trace(self, message):
        """ Logs a message with level TRACE.

        @param message: message to log
        @type message: string
        """
        self.__logger.log(logging.TRACE, str(message))
            
    def debug(self, message):
        """ Logs a message with level DEBUG.

        @param message: message to log
        @type message: string
        """
        self.__logger.debug(str(message))

    def info(self, message):
        """ Logs a message with level INFO.

        @param message: message to log
        @type message: string
        """
        self.__logger.info(str(message))

    def warning(self, message):
        """ Logs a message with level WARNING.

        @param message: message to log
        @type message: string
        """
        self.__logger.warning(str(message))

    def error(self, message):
        """ Logs a message with level ERROR.

        @param message: message to log
        @type message: string
        """
        self.__logger.error(str(message))

    def critical(self, message):
        """ Logs a message with level CRITICAL.

        @param message: message to log
        @type message: string
        """
        self.__logger.critical(str(message))

    def exception(self, message=""):
        """ Logs a message within an exception.

        @param message: message to log
        @type message: string
        """
        #self.__logger.exception(message)

        tracebackString = StringIO.StringIO()
        traceback.print_exc(file=tracebackString)
        message += "\n"+tracebackString.getvalue().strip()
        tracebackString.close()
        self.log(logging.EXCEPTION, str(message))

    def log(self, level, message, *args, **kwargs):
        """ Logs a message with given level.

        @param level: log level to use
        @type level: int

        @param message: message to log
        @type message: string
        """
        self.__logger.log(level, str(message), *args, **kwargs)

    def shutdown(self):
        """ Shutdown the logging service.
        """
        logging.shutdown()
