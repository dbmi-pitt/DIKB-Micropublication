## query-DIKB-DDIs.py
##
## Simple Python script to query http://dbmi-icode-01.dbmi.pitt.edu:2020/sparql for DIKB observed DDIs"
## No extra libraries required.

# Authors: Richard D Boyce, Yifan Ning
#
# August 2014
# 

## This code is licensed under Apache License Version 2.0, January
## 2004. Please see the license in the root folder of this project


import json
import urllib2
import urllib
import traceback
#import pickle
import csv
import sys
reload(sys);
sys.setdefaultencoding("utf8")

sys.path = sys.path + ['.']


from PDDI_Model import getPDDIDict

def query(q,epr,f='application/sparql-results+json'):
    """Function that uses urllib/urllib2 to issue a SPARQL query.
       By default it requests json as data format for the SPARQL resultset"""

    try:
        params = {'query': q}
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

if __name__ == "__main__":

    # load all observed DDIs
    pddiDictL = []
    sparql_service = "http://dbmi-icode-01.dbmi.pitt.edu/dikb/sparql"
    
    query_string = """ 
PREFIX swanpav: <http://purl.org/swan/1.2/pav/>
PREFIX meta: <http://www4.wiwiss.fu-berlin.de/bizer/d2r-server/metadata#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prvTypes: <http://purl.org/net/provenance/types#>
PREFIX swandr: <http://purl.org/swan/1.2/discourse-relationships/>
PREFIX d2r: <http://sites.wiwiss.fu-berlin.de/suhl/bizer/d2r-server/config.rdf#>
PREFIX map: <file:////home/rdb20/Downloads/d2r-server-0.7-DIKB/mapping.n3#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX swande: <http://purl.org/swan/1.2/discourse-elements#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX prv: <http://purl.org/net/provenance/ns#>
PREFIX db: <http://dbmi-icode-01.dbmi.pitt.edu:2020/resource/>
PREFIX siocns: <http://rdfs.org/sioc/ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX prvFiles: <http://purl.org/net/provenance/files#>
PREFIX ndfrt: <http://purl.bioontology.org/ontology/NDFRT/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX ncbit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
PREFIX dikbEvidence: <http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#>
PREFIX dikbD2R: <http://dbmi-icode-01.dbmi.pitt.edu:2020/vocab/resource/>
PREFIX swanco: <http://purl.org/swan/1.2/swan-commons#>
PREFIX prvIV: <http://purl.org/net/provenance/integrity#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX swanci: <http://purl.org/swan/1.2/citations/>

SELECT DISTINCT * WHERE {
  ?s a dikbD2R:DDIObservation;
     dikbD2R:PharmacokineticDDIAssertion ?asrt;
     dikbD2R:ObjectDrugOfInteraction  ?object;
     dikbD2R:PrecipitantDrugOfInteraction ?precip;
     rdfs:label ?label.

  ?object a ncbit:Pharmacologic_Substance;
     owl:sameAs ?objectURI.

  ?precip a ncbit:Pharmacologic_Substance;
     owl:sameAs ?precipURI.

  ?asrt a swande:ResearchStatement;
    foaf:homepage ?homepage;
    dikbD2R:Assertions_numeric_val ?numericVal;
    dikbD2R:Assertions_cont_val ?contVal;
    dikbD2R:slot  ?ddiPkEffect;
    swanco:citesAsSupportingEvidence ?evidence;
    rdfs:label ?researchStatementLabel.
    
  ?evidence a ncbit:Evidence;
   dikbEvidence:Evidence_type ?evType;
   rdfs:seeAlso ?evSource;
   siocns:content ?content;
   dc:date ?dateAnnotated;
   dc:creator ?whoAnnotated. 

   
   ?evidence dikbD2R:Evidence_object_dose ?objectDose. 

   ?evidence dikbD2R:Evidence_precip_dose ?precipDose.
  
   ?evidence dikbD2R:Evidence_numb_subjects ?numOfSubjects.
  
}
     
"""
    print "OBSERVED DDIs query_string: %s" % query_string
    json_string = query(query_string, sparql_service)
    
    resultset=json.loads(json_string)

    #print resultset.values()
    print str(len(resultset["results"]["bindings"]))
    

    if len(resultset["results"]["bindings"]) == 0:
        print "INFO: No result!"
    else:
        #print json.dumps(resultset,indent=1)
        for i in range(0, len(resultset["results"]["bindings"])):
        #for i in range(10, 11):
             newPDDI = getPDDIDict()
             newPDDI["evidence"] = resultset["results"]["bindings"][i]["evidence"]["value"].encode("utf8")
             newPDDI["researchStatement"] = resultset["results"]["bindings"][i]["asrt"]["value"].encode("utf8")
             newPDDI["uri"] = resultset["results"]["bindings"][i]["s"]["value"].encode("utf8")

             obj =  resultset["results"]["bindings"][i]["object"]["value"].encode("utf8")
             newPDDI["object"] = obj.replace(u"http://dbmi-icode-01.dbmi.pitt.edu/dikb/resource/Drugs/",u"").upper().encode("utf8")

             precip = resultset["results"]["bindings"][i]["precip"]["value"].encode("utf8")
             newPDDI["precip"] = precip.replace(u"http://dbmi-icode-01.dbmi.pitt.edu/dikb/resource/Drugs/",u"").upper().encode("utf8")

             newPDDI["objectURI"] = resultset["results"]["bindings"][i]["objectURI"]["value"].encode("utf8")
             newPDDI["precipURI"] = resultset["results"]["bindings"][i]["precipURI"]["value"].encode("utf8")
             newPDDI["label"] = resultset["results"]["bindings"][i]["label"]["value"].encode("utf8")
             newPDDI["homepage"] = resultset["results"]["bindings"][i]["homepage"]["value"].encode("utf8")
             newPDDI["numericVal"] = resultset["results"]["bindings"][i]["numericVal"]["value"].encode("utf8")
             newPDDI["contVal"] = resultset["results"]["bindings"][i]["contVal"]["value"].encode("utf8")
             newPDDI["ddiPkEffect"] = resultset["results"]["bindings"][i]["ddiPkEffect"]["value"].encode("utf8")
             newPDDI["evidenceSource"] = resultset["results"]["bindings"][i]["evSource"]["value"].encode("utf8")
             newPDDI["evidenceType"] = resultset["results"]["bindings"][i]["evType"]["value"].encode("utf8")
             newPDDI["evidenceStatement"] = resultset["results"]["bindings"][i]["content"]["value"].encode("utf8")
             newPDDI["dateAnnotated"] = resultset["results"]["bindings"][i]["dateAnnotated"]["value"].encode("utf8")
             newPDDI["whoAnnotated"] = resultset["results"]["bindings"][i]["whoAnnotated"]["value"].encode("utf8")
             newPDDI["researchStatementLabel"] = resultset["results"]["bindings"][i]["researchStatementLabel"]["value"].encode("utf8")
             
             #if resultset["results"]["bindings"][i]["objectDose"]:
             newPDDI["objectDose"] = resultset["results"]["bindings"][i]["objectDose"]["value"].encode("utf8")
             #if resultset["results"]["bindings"][i]["precipDose"]:
             newPDDI["precipDose"] = resultset["results"]["bindings"][i]["precipDose"]["value"].encode("utf8")
             newPDDI["numOfSubjects"] = resultset["results"]["bindings"][i]["numOfSubjects"]["value"].encode("utf8")
             

             pddiDictL.append(newPDDI)
#    print str(pddiDictL)

#    f = open("../data/dikb-observed-ddis-test.pickle","w")
#    pickle.dump(pddiDictL, f)
#    f.close()

    ## write dict to tsv file

    with open('../data/dikb-observed-ddis.tsv', 'wb') as tsvfile:
        #writer = csv.DictWriter(tsvfile, delimiter='\t', fieldnames=["drug1","drug2","objectUri","ddiPkMechanism","contraindication","severity","source","dateAnnotated","precipUri","precaution","evidence","researchStatement",'uri',"object","precip","objectURI","precipURI","label","homepage","numericVal","contVal","ddiPkEffect","evidenceSource","evidenceType","evidenceStatement","dataAnnotated","whoAnnotated","researchStatementLabel","objectDose", "precipDose", "numOfSubjects"])

        writer = csv.DictWriter(tsvfile, delimiter='\t', fieldnames=["ddiPkMechanism","contraindication","severity","source","dateAnnotated","precaution","evidence","researchStatement",'uri',"object","precip","objectURI","precipURI","label","homepage","numericVal","contVal","ddiPkEffect","evidenceSource","evidenceType","evidenceStatement","dataAnnotated","whoAnnotated","researchStatementLabel","objectDose", "precipDose", "numOfSubjects"])

        writer.writeheader()
        for line in pddiDictL:
            writer.writerow(line)
