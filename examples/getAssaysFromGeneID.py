def getAssaysFromGeneID(geneID):
  """
  Returns a dictionary of pandas DataFrames containing the assay data for all 
  assays with AIDs assocated to geneID mapped to their respective AIDs.
  @param geneID  The geneID to search on
  """
  AIDs = getAIDsFromGeneID(geneID)
  return getAssaysFromAIDs(AIDs)
