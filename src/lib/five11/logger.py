#
import logging

_DEFAULT_LOGGING_LEVEL = logging.INFO
def create_logger(name=None):
  # create logger
  if not name:
    name = __name__
  logger = logging.getLogger(name)
  logger.setLevel(_DEFAULT_LOGGING_LEVEL)
  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(_DEFAULT_LOGGING_LEVEL)
  # create formatter
  format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  formatter = logging.Formatter(format_string)
  # add formatter to ch
  ch.setFormatter(formatter)
  # add ch to logger
  logger.addHandler(ch)
  return logger
# End of file.
