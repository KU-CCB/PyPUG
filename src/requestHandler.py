#!/bin/python

"""
lib/requestHandler.py

Web request handler for PyPUG

The request handler needs to either check the cache (database) for queries 
whose result is still stored locally and decide to retrieve the data from 
PubChem if no result is found.
"""

import requests
from requestErrors import PugRestException
import databaseManager as db
import sys

__all__ = ["get", "post"]

PugRestErrors = {
  200: { "code": "(none)",                    "message": "Success"},
  400: { "code": "PugRest.BadRequest",        "message": "Request is improperly formed"},
  404: { "code": "PugRest.NotFound",          "message": "The input record was not found"},
  405: { "code": "PugRest.MethodNotAllowed",  "message": "Request not allowed (such as invalid MIME type in the HTTP Accept header)"},
  504: { "code": "PugRest.Timeout",           "message": "The request timed out, from server overload or too broad a request"},
  501: { "code": "PugRest.Unimplemented",     "message": "The requested operation has not (yet) been implemented by the server"},
  500: { "code": "PugRest.ServerError",       "message": "Some problem on the server side (such as a database server down, etc.)"},
  414: { "code": "Unknown",                   "message": "Unknown"},
  #500: { "code": "PugRest.Unknown",           "message": "An unknown error occurred"}
}

def exit(msg="exiting."):
  # clean up
  sys.exit(msg)

def handleRequestError(e):
  sys.stderr.write("[PugRest Error]\n")
  for key, value in e.error.iteritems():
    sys.stderr.write("--%s:  %s\n" %(key, value))

def handleKeyError(error):
  sys.stderr.write("[pypug KeyError]\n")
  sys.stderr.write("--The Pug server returned an unhandled status code:")
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
      e = PugRestException(response.text, {
        'url': url,
        'code': PugRestErrors[response.status_code]["code"], 
        'message': PugRestErrors[response.status_code]["message"],
        'response': response.text.strip().replace('\n', ',')
      })
      handleRequestError(e)
      raise e
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
        e = PugRestException(response.text, {
          'url': url,
          'code': PugRestErrors[response.status_code]["code"], 
          'message': PugRestErrors[response.status_code]["message"],
          'response': response.text.strip().replace('\n', ','),
          'payload': payload
        })
        handleRequestError(e)
        raise e
      except KeyError as e:
        handleKeyError(e)
    else:
      return response.text.strip()