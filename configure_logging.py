"""configure_logging: 
Configure python logger without cluttering application code
Requirements:
    Create a python logger with parameters:
        Given name (usually the name of the calling python script)
        Log level
        Flag to indicate whether console logging should be enabled
        Flag to indicate whether file logging should be enabled 
            Log file to be named by the given log name with .log extension
    Ability to get the configured application logger in other python scripts used by application
        No need to know application logger name within other script files to get the application log 
    Standardized formatting based on application requirements
"""
__author__ = "Ramprasad Polana"
__email__ = "rpolana@yahoo.com"
__license__ = "Unlicense: See the accompanying LICENCE file for details"
__copyright__ = "Anti-Copyright Waiver: The author of this work hereby waives all claim of copyright (economic and moral) in this work and immediately places it in the public domain; it may be used, distorted or destroyed in any manner whatsoever without further attribution or notice to the creator."
__date__ = "Dec 2021"
__version__ = "1.0"
__status__ = "Development"

import os
import logging

LOG_EXTENSION = r'.log'
global_application_loggers = None

def configure_log(logname, log_level = 'INFO', log_to_console_flag = True, log_to_file_flag = False):
    # logging.basicConfig()
    global global_application_loggers
    logger_name = os.path.splitext(os.path.basename(logname))[0]
    log = logging.getLogger(logger_name)
    log.setLevel(os.environ.get("PYTHON_LOGLEVEL", log_level))
    class OneLineExceptionFormatter(logging.Formatter):
        def formatException(self, exc_info):
            result = super().formatException(exc_info)
            return repr(result)
    
        def format(self, record):
            result = super().format(record)
            if record.exc_text:
                result = result.replace("\n", "")
            return result
    formatter = OneLineExceptionFormatter(logging.BASIC_FORMAT)
    ## formatter = logging.BASIC_FORMAT
    if log_to_console_flag:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)
    ## import logging.handlers
    ## LOG_FILENAME_DEFAULT = '/var/log/python.log'
    ## sys_file_handler = logging.handlers.WatchedFileHandler(os.environ.get("PYTHON_LOGFILE", LOG_FILENAME_DEFAULT))
    if log_to_file_flag:
        log_filename = logname + LOG_EXTENSION
        file_handler = logging.FileHandler(os.environ.get("PYTHON_LOGFILE", log_filename))
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    if global_application_loggers is None:
        global_application_loggers = {}
    global_application_loggers['logname'] = log
    return log

def get_application_logger(logname = None):
    global global_application_loggers
    if global_application_loggers is None:
        global_application_loggers = {}
    if logname is None:
        logger = next(iter(global_application_loggers.values()))
        if logger is None:
            raise Exception(f'get_application_logger(): No application loggers configured')
    else:
        logger = global_application_loggers[logname]
        if logger is None:
            raise Exception(f'get_application_logger(): No application logger configured by name {logname}')