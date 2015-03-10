import sys, os, datetime
sys.path.append('.')
from SPARQLWrapper import SPARQLWrapper, JSON


QUERIES_PATH = "../queries/"

def readCSVfromDir(inputdir):
    queriesD = {}

    for fname in os.listdir(inputdir):
        if fname.endswith(".sparql"):
            with open(inputdir + fname) as f:
                query = f.read()
                queriesD[fname] = query

    return queriesD


################################################################################
## MAIN TESTING
################################################################################

queriesD = readCSVfromDir(QUERIES_PATH)
#sparql = SPARQLWrapper("http://dbmi-icode-01.dbmi.pitt.edu/sparql")


sparql = SPARQLWrapper("https://dbmi-icode-01.dbmi.pitt.edu/sparql")
sparql.method = 'POST'

for name,qry in queriesD.items():
    
 #   print "[INFO] testing query (%s): \n %s" % (name, qry)

    try:

        sparql.setQuery(qry)    
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        print len(results["results"]["bindings"])
    
        if len(results["results"]["bindings"]) == 0:
            print "[WARN] Query : %s is not getting any results back" % (name) 
        else:
            print "[INFO] Query : %s is validated" % (name) 

    except:
        print "[DEBUG] Query %s is not a correct query or not getting any results back" % (name)
