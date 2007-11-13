import logging
import sys

Logger = logging.getLogger()
Logger.setLevel(logging.DEBUG)

Logger.addHandler(logging.StreamHandler(sys.stdout))

