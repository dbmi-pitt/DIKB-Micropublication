## READ ALL QUERIES FROM FOLDER query/, EXECUTE ALL QUERIES UPON MP GRAPH WITH DIFFERENT FOLDS
 
## Authors:
## Yifan Ning

import sys, os, datetime
import time
sys.path.append('.')
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

################################################################################
# Globals
################################################################################
QUERIES_PATH = "../queries/benchmark-queries/"

#sparql = SPARQLWrapper("http://dbmi-icode-01.dbmi.pitt.edu/sparql")
sparql = SPARQLWrapper("https://dbmi-icode-01.dbmi.pitt.edu/sparql")
#sparql = SPARQLWrapper("http://localhost:8890/sparql")



################################################################################
# Functions
################################################################################

def getGraphDict():
    return {"name":None, "fold":None, "cost":None, "triples":None}

def readCSVfromDir(inputdir):
    queriesD = {}

    for fname in os.listdir(inputdir):
        if fname.endswith(".sparql"):
            with open(inputdir + fname) as f:
                query = f.read()
                queriesD[fname] = query

    return queriesD


def readGraphConfig():

    graphD = dict(line.strip().split('=') for line in open('graph-config.properties'))
    return graphD


def runQuery(qry, graphname):

    #try:
    qry = qry.replace("graph",graphname)

    # print "[INFO] testing query on graph (%s): \n %s" % (graphname, qry)

    st1 = time.time()
    
    sparql.setQuery(qry)    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    st2 = time.time()
    st3 = st2 - st1

    if len(results["results"]["bindings"]) == 0:
        print "[DEBUG] Query is not getting any results back"
    else:
        print "[INFO] Query return %s results \n time cost: %s" % (len(results["results"]["bindings"]), str(st3))

    return str(st3)
    #except:
    #    print "[DEBUG] Query is not a correct query or not getting any results back"
    
    

def runAllQueries(queryFolder):
    
    queriesD = readCSVfromDir(queryFolder)

    sparql.method = 'POST'

    for qryName,qry in queriesD.items():

        if qry.strip() == "":
            #print "[WARN] skip empty query %s" % qryName
            continue

        print "[QUERY] %s" % qryName
        
        analysisD = {}

        ## run query on graphs with different folds
        graphsD = readGraphConfig()

        print graphsD
        
        for k,graphName in graphsD.items():
            
            analysisD[graphName] = {}
            
            cost = runQuery(qry, graphName)
            
            analysisD[graphName]["fold"] = k
            analysisD[graphName]["cost"] = cost

        print analysisD
        print "\n"
            

################################################################################
## MAIN TESTING
################################################################################


if __name__ == "__main__":
    readGraphConfig()
    runAllQueries(QUERIES_PATH)
    
