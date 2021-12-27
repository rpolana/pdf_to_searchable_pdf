import os, sys, logging

LOG_EXTENSION = r'.log'
def configure_log(logname, log_level = 'INFO', log_to_console_flag = True, log_to_file_flag = False):
    # logging.basicConfig()
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
    return log
