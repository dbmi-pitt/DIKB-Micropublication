import json as simplejson
from SPARQLWrapper import SPARQLWrapper, JSON
import json,urllib2,urllib,traceback, sys

FDAPreferredSubstanceToUNII = ""

if len(sys.argv) > 1:
    FDAPreferredSubstance = str(sys.argv[1])
else:
    print "Usage: getChebiMappingsFromJSON.py <path to FDAPreferredSubstanceToUNII.txt>"
    sys.exit(1)

# add manually query into script
# f = open("bioportal_sparql_results_10202014.json","r")
# labelsD = simplejson.load(f)

def query(q,apikey,epr,f='application/json'):
    """Function that uses urllib/urllib2 to issue a SPARQL query.
       By default it requests json as data format for the SPARQL resultset"""

    try:
        params = {'query': q, 'apikey': apikey}
        params = urllib.urlencode(params)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr+'?'+params)
        request.add_header('Accept', f)
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        return url.read()
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        raise e

qry = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT *
FROM <http://bioportal.bioontology.org/ontologies/CHEBI> 
WHERE 
{
  ?x <http://www.geneontology.org/formats/oboInOWL#hasRelatedSynonym> ?label.     
}
"""

sparql_service = "http://sparql.bioontology.org/sparql/"

#To get your API key register at http://bioportal.bioontology.org/accounts/new
api_key = "74028721-e60e-4ece-989b-1d2c17d14e9c"

#print "query_string: %s" % qry
json_string = query(qry, api_key, sparql_service)
resultset=json.loads(json_string)

#print "ResultSet:" + str(resultset)

if len(resultset["results"]["bindings"]) == 0:
    print "INFO: No result for %s" % d
else:
    labToUriD = {}
    for bnd in resultset["results"]["bindings"]:

        uri = bnd["x"]["value"]
        label = bnd["label"]["value"]
        labToUriD[label] = uri

        f = open(FDAPreferredSubstance, "r")

    dl = [x.strip('\r\n') for x in f.readlines()]

    f.close()

    nameToChebiD = {}
    for d in dl:

        #print "[INFO] Query drug " + d
        if labToUriD.get(d.upper()):
            nameToChebiD[d] = labToUriD.get(d.upper())
            continue
        elif labToUriD.get(d.lower()):
            nameToChebiD[d] = labToUriD.get(d.lower())
            continue
        elif labToUriD.get(d.lower().capitalize()):
            nameToChebiD[d] = labToUriD.get(d.lower().capitalize())
            continue
        else:
            nameToChebiD[d] = "No found ChEBI URI"
            #print "[WARNING]: No match for %s found in ChEBI synonyms" % d

#print "\n\nRESULTS:"

    for k,v in nameToChebiD.iteritems():
        print "%s	%s" % (k,v)
