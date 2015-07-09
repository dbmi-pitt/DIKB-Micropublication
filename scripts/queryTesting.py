## READ ALL QUERIES FROM FOLDER query/, EXECUTE ALL QUERIES UPON MP GRAPH WITH DIFFERENT FOLDS
 
## Authors:
## Yifan Ning

import sys, os, datetime
import time,csv
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
    return {"graphname":None, "cost":None, "triples":None}

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


def countTriplesFromGraph(graphname):

    qry = """
    SELECT (count(*) as ?count) 
    FROM <%s>
    WHERE {
   ?s ?p ?o . }
    """ % (graphname)

    sparql.setQuery(qry)    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return results["results"]["bindings"][0]["count"]["value"]



def runQuery(qry, graphname):

    #try:
    qry = qry.replace("graph",graphname)

    # print "[INFO] testing query on graph (%s): \n %s" % (graphname, qry)


    
    sparql.setQuery(qry)    
    sparql.setReturnFormat(JSON)

    st1 = time.time()
    results = sparql.query().convert()

    st2 = time.time()
    st3 = st2 - st1

    if len(results["results"]["bindings"]) == 0:
        print "[DEBUG] Query is not getting any results back"
        return "No results"
    else:
        print "[INFO] Query return %s results \n time cost: %s" % (len(results["results"]["bindings"]), str(st3))

    return str(st3)
    #except:
    #    print "[DEBUG] Query is not a correct query or not getting any results back"
    
    

def runAllQueries(queryFolder):
    
    queriesD = readCSVfromDir(queryFolder)
    sparql.method = 'POST'
    
    with open ("queryBenchmark.csv","wb") as csvfile:

        spamwriter = csv.writer(csvfile, delimiter='|', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        ## read all queries
        for qryName,qry in queriesD.items():

            if qry.strip() == "":
                continue

            print "[QUERY] %s" % qryName

            outputLineD = {}

            ## run query on graphs that have different folds
            graphsD = readGraphConfig()

            ## execute query for different folds of graphs
            for k,graphName in graphsD.items():

                graphD = getGraphDict()

                cost = runQuery(qry, graphName)
                triples = countTriplesFromGraph(graphName)

                graphD["cost"] = cost
                graphD["triples"] = triples
                graphD["graphname"] = graphName

                outputLineD[k] = graphD

            print outputLineD

            ## write header for query
            spamwriter.writerow([qryName, "Number of folds", "triples" ,"costs"])

            ## write graphname, triples, costs for current query
            for i in range (0 , len(graphsD)):
                foldStr = str(i)
                spamwriter.writerow([outputLineD[foldStr]["graphname"], foldStr, outputLineD[foldStr]["triples"], outputLineD[foldStr]["cost"]])

            print "\n\n"
            

################################################################################
## MAIN TESTING
################################################################################


if __name__ == "__main__":
    readGraphConfig()
    runAllQueries(QUERIES_PATH)
    
