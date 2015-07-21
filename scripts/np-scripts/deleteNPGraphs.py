import sys, os
from subprocess import Popen, PIPE
from textwrap import dedent
import tempfile
import subprocess
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
from isql_connector import ISQLWrapper

def getNPGraphByTypeQry(type):
    qry = """
    PREFIX np: <http://www.nanopub.org/nschema#>
    SELECT DISTINCT ?s
    WHERE { ?s a np:%s.}

    """ % (type)
    return qry

def getNPAssertIndxQry():
    qry = """
    PREFIX np: <http://www.nanopub.org/nschema#>
    PREFIX mp: <http://purl.org/mp/>
    SELECT ?s
    WHERE
    {
    ?s rdf:type np:assertion.
    ?m np:hasAssertion ?s.
    }
    """
    return qry


def getListOfURIsByQry(qry, sparql_service):
    
    npsparql = SPARQLWrapper(sparql_service)

    npsparql.setQuery(qry)
    npsparql.setReturnFormat(JSON)
    resultset = npsparql.query().convert()
    
    nanopubL = []
    if len(resultset["results"]["bindings"]) == 0:
        print "INFO: No result!"
    else:
        for i in range(0, len(resultset["results"]["bindings"])):
            nanopubL.append(resultset["results"]["bindings"][i]["s"]["value"].strip())
    return nanopubL


def deleteListOfGraphsISQL(URIsL):

    isql = ISQLWrapper("localhost","dba","dba")

    for uri in URIsL:
        graphname = uri.replace("http://purl.obolibrary.org/obo/","obo:") 
        print "[INFO] delete graph " + graphname
        isql.clean_graph(graphname)

    
def deleteGraphByIdx(name, sparql_service):

    qry = getNPAssertIndxQry()
    npIdxL = getListOfURIsByQry(qry, sparql_service)

    graphL = []
    for npIdx in npIdxL:
        graphL.append(npIdx + name)
    
    deleteListOfGraphsISQL(graphL)
    #print npIdxL


def deleteGraphByType(type, sparql_service):

    qry = getNPGraphByTypeQry(type)
    graphL = getListOfURIsByQry(qry, sparql_service)
    deleteListOfGraphsISQL(graphL)

    
if __name__ == "__main__":

    #sparql_service = "https://dbmi-icode-01.dbmi.pitt.edu/dikb/sparql"
    sparql_service = "http://localhost:8890/sparql"

    ## delete graphs np-head 
    deleteGraphByIdx("-head", sparql_service)
    
    deleteGraphByType("Nanopublication", sparql_service)
    deleteGraphByType("assertion", sparql_service)
    deleteGraphByType("Provenance", sparql_service)
    deleteGraphByType("PublicationInfo", sparql_service)

    npGraphL = ['ns1:default']
    deleteListOfGraphsISQL(npGraphL)
