#!/bin/python

# every function should return a dictionary mapping the search key to it's returned
# value as either a list or a dataframe.

# Need to implement getSIDsFromAIDs

import sys
sys.path.append("./src")
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
from requestHandler import get, post
import requestErrors
import pandas as pd

PROLOG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
ENCODING = "utf-8"
PugRestException = requestErrors.PugRestException

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
  url = PROLOG + ("/assay/aid/%s/description/JSON" % AID)
  response = get(url) # needs to be parsed into an object
  return response

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