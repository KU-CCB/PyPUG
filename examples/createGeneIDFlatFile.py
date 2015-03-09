import sys
import socket
if socket.gethostname()[-6:] == "ku.edu":
	sys.path.append('/usr/lib/python2.6/site-packages/')
import os
from datetime import date
from operator import itemgetter
import zipfile
import gzip
import json
import math
import mysql.connector
from mysql.connector import errorcode
from mysql.connector.constants import ClientFlag
import pypug

"""
File 1
------
>geneid
aid
aid
aid
...

pypug version
database version
"""

host, user, passwd, db = sys.argv[1:5]
geneids = sys.argv[5:]#[1815, 1816]
print geneids

pypugFile1 = "geneid.aid.pypug.txt"
pypugFile2 = "geneid.fullassay.pypug.txt"
ccbFile1   = "geneid.aid.ccb.txt"
ccbFile2   = "geneid.fullassay.ccb.txt"

# -- PyPug File 1 --

with open(pypugFile1, 'w') as outfile:
  for i in range(0, len(geneids)):
    # Get all aids associated with this geneid from PUG
    # and write the geneid header followed by each id
    aids = pypug.getAIDsFromGeneID(geneids[i])
    outfile.write(">%s\n" % geneids[i])
    for j in range(0, len(aids)):
      sys.stdout.write(("\rWriting aid (%03d/%03d) for gene (%02d/%02d)" %
        (j+1, len(aids), i+1, len(geneids))))
      sys.stdout.flush()
      outfile.write("%s\n" % aids[j])
  sys.stdout.write('\n')

# -- CCB File 1 -- 

with open(ccbFile1, 'w') as outfile:
  # Get all assay ids associated with this geneid from the database
  cnx = mysql.connector.connect(host=host, user=user, passwd=passwd, db=db, client_flags=[ClientFlag.LOCAL_FILES])
  cursor = cnx.cursor()
  for i in range(0, len(geneids)):
    outfile.write(">%s\n" % geneids[i])
    query = "SELECT DISTINCT(assay_id) FROM Aid2GiGeneidAccessionUniprot WHERE gene_id=%s" % geneids[i]
    cursor.execute(query)
    # Load the list of aids
    aids = map(itemgetter(0), cursor.fetchall())
    for j in range(0, len(aids)):
      sys.stdout.write(("\rWriting aid (%03d/%03d) for gene (%02d/%02d)" %
        (j+1, len(aids), i+1, len(geneids))))
      sys.stdout.flush()
      outfile.write("%s\n" % aids[j])
  sys.stdout.write('\n')
  cnx.close()


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

pypug version
ccb version
"""

# -- PyPug File 2 --

with open(pypugFile1, 'r') as infile:
  with open(pypugFile2, 'w') as outfile:
    i = 0
    for line in infile:
      i += 1
      sys.stdout.write("\r> processing lines (%03d)" % i)
      sys.stdout.flush()
      line = line.rstrip()
      if line[0] is '>':
        outfile.write("%s\n" % line) # geneid
      else:
        aid = line
        assay = pypug.getAssayFromSIDs(aid)
        outfile.write("$%s\n" % aid)
        for sid, cid, outcome in zip(assay["PUBCHEM_SID"], assay["PUBCHEM_CID"], assay["PUBCHEM_ACTIVITY_OUTCOME"]):
          if math.isnan(cid): # cid is unavailable
            cid, smiles = "","" # empty values since no cid
          else:
            smiles = pypug.getCanonicalSMILESFromCID(cid)
          outfile.write("%s\t%s\t%s\t" % sid, cid, smiles)
          outfile.write("\n");
    sys.stdout.write('\n')

# -- CCB File 2 -- #INCOMPLETE
"""
with open(ccbFile1, 'r') as infile:
  cnx = mysql.connector.connect(host=host, user=user, passwd=passwd, db=db, client_flags=[ClientFlag.LOCAL_FILES])
  cursor = cnx.cursor()
  with open(ccbFile2, 'w') as outfile:
    i = 0
    for line in infile:
      i += 1
    sys.stdout.write("\r> processing lines (%03d)" % i)
    sys.stdout.flush()
    line = line.rstrip()
    if line[0] is '>':
      outfile.write("%s\n" % line) # geneid
    else:
      aid = line
      cursor.execute((
        "SELECT Bioassays.substance_id, Bioassays.activity_outcome,"
        "       Substance_id_compound_id.compound_id,"
        "FROM Bioassays "
        "WHERE Bioassays.aid='%s' "
        "AND Substance_id_compound_id.substance_id=Bioassays.substance_id"), aid)
      print(cursor.fetchall())
"""
