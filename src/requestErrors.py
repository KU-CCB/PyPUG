import sys

def exit(msg="exiting."):
  sys.exit(msg)

def handleRequestError(e):
  sys.stderr.write("[PUGREST Error]\n")
  for key, value in e.error.iteritems():
    sys.stderr.write("--%s:  %s\n" %(key, value))
  exit()

class PUGRESTException(Exception):
  def __init__(self, message, error=None):
    super(PUGRESTException, self).__init__(message)
    self.error = error