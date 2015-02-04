#!/bin/python

"""
lib/requestHandler.py

Web request handler for pyPUG

The request handler needs to either check the cache (database) for queries 
whose result is still stored locally and decide to retrieve the data from 
PubChem if no result is found.
"""

import requests
from requestErrors import PUGRESTException, exit
import databaseManager as db
import sys

__all__ = ["get", "post"]

PUGRESTErrors = {
  200: { "code": "(none)",                    "message": "Success"},
  400: { "code": "PUGREST.BadRequest",        "message": "Request is improperly formed"},
  404: { "code": "PUGREST.NotFound",          "message": "The input record was not found"},
  405: { "code": "PUGREST.MethodNotAllowed",  "message": "Request not allowed (such as invalid MIME type in the HTTP Accept header)"},
  504: { "code": "PUGREST.Timeout",           "message": "The request timed out, from server overload or too broad a request"},
  501: { "code": "PUGREST.Unimplemented",     "message": "The requested operation has not (yet) been implemented by the server"},
  500: { "code": "PUGREST.ServerError",       "message": "Some problem on the server side (such as a database server down, etc.)"},
  414: { "code": "Unknown",                   "message": "Unknown"},
  #500: { "code": "PUGREST.Unknown",           "message": "An unknown error occurred"}
}

def handleKeyError(error):
  sys.stderr.write("[pypug KeyError]\n")
  sys.stderr.write("--The PUG server returned an unhandled status code:")
  sys.stderr.write("--You must add a handler for this status in requestHandler.py")
  sys.stderr.write(e)
  exit()

def get(url):
  cached = db.findByURL(url)
  if cached:
    return cached
  else: 
    response = requests.get(url)
    if str(response.status_code) != "200":
      raise PUGRESTException(response.text, {
        'url': url,
        'code': PUGRESTErrors[response.status_code]["code"], 
        'message': PUGRESTErrors[response.status_code]["message"],
        'response': response.text.strip().replace('\n', ',')
      })
    else:
      return response.text.strip()

def post(url, payload):
  cached = db.findByURL(url)
  if cached:
    return cached
  else: 
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)
    if str(response.status_code) != "200":
      try: 
        raise PUGRESTException(response.text, {
          'url': url,
          'code': PUGRESTErrors[response.status_code]["code"], 
          'message': PUGRESTErrors[response.status_code]["message"],
          'response': response.text.strip().replace('\n', ','),
          'payload': payload
        })
      except KeyError as e:
        # If this error is caught, it means that PUG returned an error with a
        # status code that has not been handled yet. You must add an entry for
        # the 3-digit status code into the PUGRESTErrors object.
        handleKeyError(e)
    else:
      return response.text.strip()