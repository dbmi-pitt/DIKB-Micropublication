import sys, os
from subprocess import Popen, PIPE
from textwrap import dedent
import tempfile
import subprocess
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
from isql_connector import ISQLWrapper

ISQL_CONFIG = "isql-connection.conf"


## delete np graphs using ddi namespace

def deleteListOfGraphsISQL(maxIdxNum, npType):

    USER = None
    PWD = None

    dbconfig = file = open(ISQL_CONFIG)
    if dbconfig:
        for line in dbconfig:
            if "USERNAME" in line:
                USER = line[(line.find("USERNAME=")+len("USERNAME=")):line.find(";")]
            elif "PASSWORD" in line:  
                PWD = line[(line.find("PASSWORD=")+len("PASSWORD=")):line.find(";")]

    if USER and PWD:
        isql = ISQLWrapper("localhost", USER, PWD)

        for i in range (1,int(maxIdxNum)):

            graphname = "ddi:ddi-spl-annotation-np-" + npType + "-" + str(i)

            print "[INFO] delete graph " + graphname
            isql.clean_graph(graphname)
    else:
        print "[DEBUG] isql connection fail, check isql_config"

## delete old np graphs using obo namespace

def deleteListOfGraphsISQLOBO(maxIdxNum, npType):

    isql = ISQLWrapper("localhost","dba","cjirtR01")

    for i in range (1,int(maxIdxNum)):

        graphname = "obo:DIDEO_XXX" + str(i) + "-" + npType

        print "[INFO] delete graph " + graphname
        isql.clean_graph(graphname)


if __name__ == "__main__":

    deleteListOfGraphsISQL(355, "head")    
    deleteListOfGraphsISQL(355, "assertion")    

    deleteListOfGraphsISQLOBO(355, "pubInfo")
    deleteListOfGraphsISQLOBO(355, "provenance")

