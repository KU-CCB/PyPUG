def getAssaysFromAIDs(AIDs, usepost=True):
  """
  Returns a dictionary of pandas DataFrames containing the assay data for all 
  assays mapped to AIDs
  @param AIDs  The list of AIDs to search on.
  @param usepost  Boolean value indicating whether post or get should be used.
  """
  assays = {}
  for AID in AIDs:
    assays[AID] = getAssayFromAID(AID, usepost)
  return assays
