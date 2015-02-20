def getAIDsFromGeneIDs(geneIDs, usepost=True):
  """
  Returns a list of lists of AIDs in the same order as geneIDs
  @param geneIDs  The list of geneIDs to search on.
  """
  AIDs = []
  for geneID in geneIDs:
    AIDs.append(getAIDsFromGeneID(geneID, usepost))
  return AIDs