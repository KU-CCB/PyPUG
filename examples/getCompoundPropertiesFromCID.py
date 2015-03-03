import pypug

"""
Retrieve a compound along with specified properties using its CID
"""
cid = 2244
properties = ["MolecularWeight", "MolecularFormula", "InChI", "CannicalSMILES"]
data = pypug.getCompoundPropertiesFromCID(cid, properties)
print data