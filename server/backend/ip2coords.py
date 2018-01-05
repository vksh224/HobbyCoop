import logging
logger = logging.getLogger("hobbycoop.geoip")

try:
  from geoip import geolite2

except:
  logger.exception("Admin needs to install geoip package:"
  "http://pythonhosted.org/python-geoip/")


def getCoordsFromIP(ip):
  try:
    match = geolite2.lookup(ip)
    return match.location

  except:
    logger.exception("Admin has not configured geoip database! Install a free"
    " one here: http://pythonhosted.org/python-geoip/")
    return (37.948889,-91.763056)
