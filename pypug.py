#!/bin/python

import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import pandas as pd
import requests

# PUG URL Prolog
PROLOG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# default encoding for strings
ENCODING = "utf-8"

# Don't report errors
SILENT = False


""" ---------------------------------------------------------------------------
Error Handling 
--------------------------------------------------------------------------- """


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

# This should be split into many different classes of errors based on PugRestErrors
class PugRestException(Exception):
  """
  Exception thrown when a request to PUG returns with a status code other than
  200 (assuming the status code is in PugRestErrors)
  """
  def __init__(self, *args, **kwargs):
    self.url = kwargs.pop('url', None)
    self.code = kwargs.pop('code', None)
    self.message = kwargs.pop('message', None)
    self.response = kwargs.pop('response', None)
    super(PugRestException, self).__init__(args, kwargs)

  def __str__(self):
    msg = (
      "--url:      "+self.url+"\n"
      "--code:     "+self.code+"\n"
      "--message:  "+self.message+"\n"
      "--response: "+self.response+"\n")
    return msg

def handleKeyError(error):
  sys.stderr.write("[pypug KeyError]\n")
  sys.stderr.write("--The Pug server returned an unhandled status code:")
  sys.stderr.write("--This status code is unhandled in pypug.py")
  sys.stderr.write(e)
  sys.exit()


""" ---------------------------------------------------------------------------
Requests Wrapper
--------------------------------------------------------------------------- """


def get(url):
  """
  Make an HTTP Get request to the PubChem ftp server
  """
  global SILENT
  response = requests.get(url)
  if str(response.status_code) != "200":
    if SILENT:
      return ""
    else:
      raise PugRestException(response.text, url=url,
              code=PugRestErrors[response.status_code]["code"],
              message=PugRestErrors[response.status_code]["message"],
              response=response.text.strip().replace('\n', ','))
  else:
    return response.text.strip()

def post(url, payload):
  """
  Make an HTTP Post request to the PubChem ftp server
  """
  global SILENT
  headers = {'content-type': 'application/x-www-form-urlencoded'}
  response = requests.post(url, data=payload, headers=headers)
  if str(response.status_code) != "200":
    if SILENT:
      return ""
    else:
      try:
        raise PugRestException(response.text, payload=payload, url=url,
                code=PugRestErrors[response.status_code]["code"],
                message=PugRestErrors[response.status_code]["message"],
                response=response.text.strip().replace('\n', ','))
      except KeyError as e:
        handleKeyError(e)
  else:
    return response.text.strip()



""" ---------------------------------------------------------------------------
PyPUG API
--------------------------------------------------------------------------- """


def SetSilent(silent):
  """
  Sets error reporting on or off. silent should be either True or False. Any 
  other values will be ignored
  @param silent  True or False
  """
  global SILENT
  if silent in (True, False):
    SILENT = silent

def getAIDsFromGeneID(geneID, usepost=True):
  """
  Returns a list of Assay IDs that have geneID as a target
  @param geneID The geneID to search on.
  @param usepost  Boolean value indicating whether post or get should be used.
  """
  response = ""
  if usepost:
    url = PROLOG + "/assay/target/GeneID/aids/TXT"
    payload = {'geneid':geneID}
    response = post(url, payload).split('\n')
  else:
    url = PROLOG + ("/assay/target/GeneID/%s/aids/TXT" % geneID)
    response = get(url).split('\n')
  return [id.encode(ENCODING) for id in response]

def getAssayFromSIDs(AID, SIDs=[]):
  """
  Returns a pandas DataFrame containing the assay data for AID. This is useful
  when an assay has more than 10000 associated SIDs and can't be retrieved with
  getAssayFromAID due to PUG data restrictions.  SIDs can be a list of the 
  prefetched SIDs for the assay or it can be an empty list, in which case the 
  SIDs for the given assay will be fetched automatically.
  @param AID  The AID to search on.
  @param SIDs  The SIDs for the given AID
  """
  response = "" 
  pos = 0
  groupSz = 9999
  if len(SIDs) < 1:
    SIDs = getSIDsFromAID(AID)
  while pos < len(SIDs):
    url = PROLOG + "/assay/aid/CSV"
    payload = {'aid':AID, 'sid':",".join(SIDs[pos:pos+groupSz])}
    pos = pos + groupSz + 1
    if len(response) == 0:
      response += post(url, payload)
    else:
      data = post(url, payload)
      response += data[data.index('\n'):]
  response = StringIO(response.encode(ENCODING))
  return pd.DataFrame.from_csv(response, index_col=False, header=0)

def getAssayFromAID(AID, usepost=True):
  """
  Returns a pandas DataFrame containing the assay data for AID.
  @param AID  The AID to search on.
  @param usepost  Boolean value indicating whether post or get should be used.
  """
  response = ""
  if usepost:
    url = PROLOG + "/assay/aid/CSV"
    payload = {'aid':AID}
    response = StringIO(post(url, payload).encode(ENCODING))
  else:
    url = PROLOG + "/assay/aid/%s/CSV" % AID
    response = StringIO(get(url).encode(ENCODING))
  return pd.DataFrame.from_csv(response, index_col=False, header=0)

def getAssayDescriptionFromAID(AID):
  """
  Return the assay description for a given AID
  @param AID  The AID to search on
  """
  #url = PROLOG + ("/assay/aid/%s/description/ASNT" % AID)
  url = PROLOG + ("/assay/aid/%s/summary/JSON" % AID) # simplified description
  response = get(url) # needs to be parsed into an object
  return response

def _getCompoundPropertiesFromCID(CID, properties):
  """
  Return the compound and its properties identified by CID
  @param CID  The CID to search on
  """
  url = PROLOG + ("/compound/cid/%s/property/%s/CSV" % (CID, ",".join(properties)))
  response = get(url)
  return response

def getCanonicalSMILESFromCID(CID):
  response = _getCompoundPropertiesFromCID(CID, ["CanonicalSMILES"])
  smiles = response.split('\n')[1].split(',')[1]
  return smiles

def getSIDsFromAID(AID, usepost=True):
  """
  Returns a list of SIDs associated with an AID.
  @param geneID The geneID to search on
  """
  response = ""
  if usepost:
    url = PROLOG + "/assay/aid/sids/TXT"
    payload = {'aid':AID}
    response = post(url, payload).split('\n')
  else:
    url = PROLOG + ("/assay/aid/%s/sids/TXT" % AID)
    response = get(url).split('\n')
  return [id.encode(ENCODING) for id in response]

def getCIDsFromAID(AID, usepost=True):
  """
  Return a list of pubchem cids that correspond to an AID.
  @param AID  The AID to search on.
  @param usepost  Boolean value indicating whether post or get should be used.
  """
  if usepost:
    url = PROLOG + "/assay/aid/cids/TXT"
    payload = {'aid':AID}
    response = post(url, payload).split('\n')
  else:
    url = PROLOG + ("/assay/aid/%s/cids/TXT" % AID)
    response = get(url).split('\n')
  return [id.encode(ENCODING) for id in response]