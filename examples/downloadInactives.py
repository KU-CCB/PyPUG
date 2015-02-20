"""
pubchem-dl-inactives.py

Retrieve all data for PubChem assays with a target of geneID.
"""
import sys
import os
import pandas as pd
import pypug

def getAssaysFromAIDs(AIDs, usepost=True):
  """
  Returns a dictionary of pandas DataFrames containing the assay data for all 
  assays mapped to AIDs
  @param AIDs  The list of AIDs to search on.
  @param usepost  Boolean value indicating whether post or get should be used.
  """
  assays = {}
  for AID in AIDs:
    assays[AID] = pypug.getAssayFromAID(AID, usepost)
  return assays

def getAssaysFromGeneID(geneID):
  """
  Returns a pandas DataFrame containing the assay data for all assays 
  corresponding to the given geneID
  @param geneID  The geneID to search on
  """
  AIDs = pypug.getAIDsFromGeneID(geneID)
  return getAssaysFromAIDs(AIDs)

# Main implementation 

if len(sys.argv) < 2:
  sys.stdout.write("Usage: pyPUG [geneID]\n")
  sys.exit()

geneID = sys.argv[1]
outputDirectory = "./assays"

if not os.path.exists(outputDirectory):
  os.makedirs(outputDirectory)
  # Ignore possible race condition now

# Use this instead of getAssaysFromGeneID when the assay contains more than 
# 10000 SIDs and won't get returned by PUG
assays = {}
AIDs = pypug.getAIDsFromGeneID(geneID)
for AID in AIDs:
  SIDs = pypug.getSIDsFromAID(AID)
  assays[AID] = pypug.getAssayFromSIDs(SIDs)

# Write Inactive data to file
for aid, data in assays.iteritems():
  data = data[data["PUBCHEM_ACTIVITY_OUTCOME"] == "Inactives"]
  data["PUBCHEM_AID"] = aid
  print "Writing %s..." % aid
  data.to_csv(outputDirectory+"/%s.csv" % aid, index=False)
  