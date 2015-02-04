import sys

class PugRestException(Exception):
  def __init__(self, message, error=None):
    super(PugRestException, self).__init__(message)
    self.error = error