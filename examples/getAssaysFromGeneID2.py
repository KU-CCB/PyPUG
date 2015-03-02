import pypug
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

user, passwd, db = "kharland", "Aldous@1", "ccb"
geneids = [1815]
dataFile1 = "file1.txt"
dataFile2 = "file2.txt"

print "starting file 1"

with open(dataFile1, 'w') as outfile:
  for geneid in geneids:
    aids = pypug.getAIDsFromGeneID(geneid)
    outfile.write(">%s\n" % geneid)
    for aid in aids:
      outfile.write("%s\n" % aid)

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

with open(dataFile1, 'r') as infile:
  with open(dataFile2, 'w') as outfile:
    for line in infile:
      line = line.rstrip()
      if line[0] is '>':
        outfile.write("%s\n" % line) # geneid
      else:
        aid = line
        assay = pypug.getAssayFromAID(aid)
        descr = pypug.getAssayDescriptionFromAID(aid).replace('\n', '')
        for outcome, cid in zip(assay["PUBCHEM_ACTIVITY_OUTCOME"], assay["PUBCHEM_CID"]):
          smiles = pypug.getCanonicalSMILESFromCID(cid)
          cnx = mysql.connector.connect(user=user, passwd=passwd, db=db, client_flags=[ClientFlag.LOCAL_FILES])
          cursor = cnx.cursor()
          try:
            query = "INSERT INTO `Bioassays`(description) VALUES('%s');" % descr
            cursor.execute(query)
            cnx.commit()
          except mysql.connector.Error as e:
            sys.stderr.write("x failed loading data: %s\n" % e)
            print smiles, cid, descr,
          finally:
            outfile.write("$%s\n" % aid)
            outfile.write("%\sn" % descr)
            outfile.write("%s\t%s\t%s\n" % (cid, smiles, descr))
                          

