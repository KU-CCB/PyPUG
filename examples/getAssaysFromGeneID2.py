import pypug
import sys
import json
import math
import mysql.connector
from mysql.connector import errorcode
from mysql.connector.constants import ClientFlag

"""
File 1
------
>geneid
aid
aid
aid
...

for id in geneids
  aids <- getAIDSFor(id)
  output ">{id}"
  for aid in aids
    output "aid\n"
"""

user, passwd, db = "kharland", "@mcdaniel1", "ccb"
geneids = [1815, 1816]
dataFile1 = "file1.txt"
dataFile2 = "file2.txt"

print "starting file 1"

with open(dataFile1, 'w') as outfile:
  for i in range(0, len(geneids)):
    aids = pypug.getAIDsFromGeneID(geneids[i])
    outfile.write(">%s\n" % geneids[i])
    for j in range(0, len(aids)):
      sys.stdout.write(("\rWriting aid (%03d/%03d) for gene (%02d/%02d)" %
        (j+1, len(aids), i+1, len(geneids))))
      sys.stdout.flush()
      outfile.write("%s\n" % aids[j])
  sys.stdout.write('\n')

"""
File 2
------

while there are still geneids
  geneid <- next geneid
  output ">{geneid}\n"
  while geneid has aids left
    aid <- next aid
    assay <- getAssayFrom(aid)
    description <- assay description with \n removed
    CID <- assay cid
    SMILES <- assay canonical smiles
    outcome <- assay outcome
    output "${aid}\n"
    output "{description}\n"
    output "{CID}\t{SMILES}\t{outcome}\n"
"""

print "starting file 2"

# with open(dataFile1, 'r') as infile:
#   with open(dataFile2, 'w') as outfile:
#     i = 0
#     for line in infile:
#       i += 1
#       sys.stdout.write("\r> processing lines (%03d)" % i)
#       sys.stdout.flush()
#       line = line.rstrip()
#       if line[0] is '>':
#         outfile.write("%s\n" % line) # geneid
#       else:
#         aid = line
#         assay = pypug.getAssayFromSIDs(aid)
#         description = json.dumps(pypug.getAssayDescriptionFromAID(aid))
#         outfile.write("$%s\n" % aid)
#         outfile.write("%s\n" % description)
#         for sid, cid, outcome in zip(assay["PUBCHEM_SID"], assay["PUBCHEM_CID"], assay["PUBCHEM_ACTIVITY_OUTCOME"]):
#           if math.isnan(cid): # cid is unavailable
#             cid, smiles = "","" # empty values since no cid
#           else:
#             smiles = pypug.getCanonicalSMILESFromCID(cid)
#           outfile.write("%s\t" % sid)
#           outfile.write("%s\t" % cid)
#           outfile.write("%s\t" % smiles)
#           outfile.write("\n");
#     sys.stdout.write('\n')

print "loading mysql table with descriptions"

with open(dataFile1, 'r') as infile:
  with open(dataFile2, 'w') as outfile:
    i = 0
    for line in infile:
      i += 1
      sys.stdout.write("\r> processing lines (%03d)" % i)
      sys.stdout.flush()
      line = line.rstrip()
      if line[0] is '>':
        pass
      else:
        aid = line
        # Remove whitespace in response using json.loads and json.dumps
        description = json.dumps(json.loads(
          pypug.getAssayDescriptionFromAID(aid).encode('utf-8')), 
          separators=(',', ': '))
        try:
          cnx = mysql.connector.connect(
            user=user, passwd=passwd, db=db, client_flags=[ClientFlag.LOCAL_FILES])
          cursor = cnx.cursor()
          query = "INSERT INTO `Assay_id_assay_description`(assay_id, assay_description) VALUES(%s,%s);"
          cursor.execute(query, (aid, description))
          cnx.commit()
        except mysql.connector.Error as e:
          sys.stderr.write("x failed loading data: %s\n" % e)
    