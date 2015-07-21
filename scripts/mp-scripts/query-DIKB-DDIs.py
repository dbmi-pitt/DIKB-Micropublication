## query-DIKB-DDIs.py
##
## Simple Python script to query http://dbmi-icode-01.dbmi.pitt.edu:2020/sparql for DIKB observed DDIs"
## No extra libraries required.

# Authors: Yifan Ning
#
# Jun 2015
# 

## This code is licensed under Apache License Version 2.0, January
## 2004. Please see the license in the root folder of this project


import json
import urllib2
import urllib
import traceback
#import pickle
import csv
import sys, copy
reload(sys);
sys.setdefaultencoding("utf8")

sys.path = sys.path + ['.']


from PDDI_Model import getAssertionDict
from PDDI_Model import getIncreaseAUCDict


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


def dikbPrefixQry():
    prefix_string = """
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

"""
    return prefix_string


## return Qry for generic type of assertions (ex. substrate_of, inhibits)
def assertionQry(assertType, evidenceMode, num):

    if not evidenceMode or not assertType:
        return None
    else:
        query_string = """

  SELECT DISTINCT * WHERE {

  ?asrt a swande:ResearchStatement;
    foaf:homepage ?homepage;
    dikbD2R:slot dikbD2R:%s;
    dikbD2R:object ?objectURI;
    dikbD2R:value ?valueURI;
    rdfs:label ?researchStatementLabel.

  # ?s dikbD2R:%s ?valueURI;
  #    rdfs:label ?label.

    ## evidenceSupports
    optional {
    ?asrt swanco:%s ?evidence.
    ?evidence dikbEvidence:Evidence_type ?evType;
              dc:creator ?whoAnnotated;
              dc:date ?dateAnnotated;
              rdfs:seeAlso ?evSource;
              siocns:content ?content.
    }
  
} LIMIT %s
""" % (assertType, assertType, evidenceMode, num)
        return dikbPrefixQry() + query_string

## return Qry for does_not_inhibit, which don't have dikbD2R:slot
def  doseNotInhibitQry(evidenceMode, num):

    if not evidenceMode:
        return None
    else:
        query_string = """

  SELECT DISTINCT * WHERE {

  ?asrt a swande:ResearchStatement;
    foaf:homepage ?homepage;
    dikbD2R:object ?objectURI;
    dikbD2R:value ?valueURI;
    rdfs:label ?researchStatementLabel.
    FILTER regex(str(?researchStatementLabel), "does_not_inhibit")

  # ?s dikbD2R:does_not_inhibit ?valueURI;
  #    rdfs:label ?label.

    ## evidenceSupports
    optional {
    ?asrt swanco:%s ?evidence.
    ?evidence dikbEvidence:Evidence_type ?evType;
              dc:creator ?whoAnnotated;
              dc:date ?dateAnnotated;
              rdfs:seeAlso ?evSource;
              siocns:content ?content.
    }
  
} LIMIT %s
""" % (evidenceMode, num)
        return dikbPrefixQry() + query_string
    


# return Qry for assertion with evidence by type increase_auc
def increaseAucQry(evidenceMode, num):

    if not evidenceMode:
        return None
    else:
        query_string = """

  ## assertion - increase auc
  SELECT DISTINCT * WHERE {

  ?s a dikbD2R:DDIObservation;
     dikbD2R:PharmacokineticDDIAssertion ?asrt;
     dikbD2R:ObjectDrugOfInteraction  ?object;
     dikbD2R:PrecipitantDrugOfInteraction ?precip;
     rdfs:label ?label.

  ?asrt a swande:ResearchStatement;
    foaf:homepage ?homepage;
    dikbD2R:slot dikbD2R:increases_auc;
    dikbD2R:value ?valueURI;
    rdfs:label ?researchStatementLabel;
    dikbD2R:object ?objectURI;
    dikbD2R:value ?precipURI;
    dikbD2R:Assertions_cont_val ?contVal;
    dikbD2R:Assertions_numeric_val ?numericVal.

    ## evidenceSupports
    optional {
    ?asrt swanco:%s ?evidence.
    ?evidence dikbEvidence:Evidence_type ?evType;
              dc:creator ?whoAnnotated;
              dc:date ?dateAnnotated;
              dikbD2R:Evidence_value ?evidenceVal;
              dikbD2R:Evidence_numb_subjects ?numOfSubjects;
              dikbD2R:Evidence_object_dose ?objectDose;
              dikbD2R:Evidence_precip_dose ?precipDose;
              rdfs:seeAlso ?evSource;
              siocns:content ?content.
    }

  
} LIMIT %s

""" % (evidenceMode, num)

    return dikbPrefixQry() + query_string


def queryIncreaseAuc(evMode, num):

    evidenceMode = None
    if evMode is "support":
        evidenceMode = "citesAsSupportingEvidence"
    elif evMode is "refute":
        evidenceMode = "citesAsRefutingEvidence"

    # load all observed DDIs
    pddiDictL = []

    sparql_service = "https://dbmi-icode-01.dbmi.pitt.edu/dikb/sparql"
    query_string = increaseAucQry(evidenceMode, num)

    print "[INFO] increases AUC query_string: %s" % query_string
    json_string = query(query_string, sparql_service)
    
    resultset=json.loads(json_string)
    print "[INFO] Number of results: " + str(len(resultset["results"]["bindings"]))

    if len(resultset["results"]["bindings"]) == 0:
        print "INFO: No result!"
    else:
        #print json.dumps(resultset,indent=1)
        for i in range(0, len(resultset["results"]["bindings"])):

             newPDDI = getIncreaseAUCDict()
             newPDDI["assertType"] = "increases_auc"
             #newPDDI["researchStatement"] = resultset["results"]["bindings"][i]["asrt"]["value"].encode("utf8")
             newPDDI["researchStatementLabel"] = resultset["results"]["bindings"][i]["researchStatementLabel"]["value"].encode("utf8")
             newPDDI["objectURI"] = resultset["results"]["bindings"][i]["objectURI"]["value"].encode("utf8")
             newPDDI["valueURI"] = resultset["results"]["bindings"][i]["precipURI"]["value"].encode("utf8")

             newPDDI["homepage"] = resultset["results"]["bindings"][i]["homepage"]["value"].encode("utf8")

             if resultset["results"]["bindings"][i].has_key("whoAnnotated"):
                 newPDDI["whoAnnotated"] = resultset["results"]["bindings"][i]["whoAnnotated"]["value"].encode("utf8")

             if resultset["results"]["bindings"][i].has_key("dateAnnotated"):
                 newPDDI["dateAnnotated"] = resultset["results"]["bindings"][i]["dateAnnotated"]["value"].encode("utf8")

             if resultset["results"]["bindings"][i].has_key("evidence"):
                 newPDDI["evidence"] = resultset["results"]["bindings"][i]["evidence"]["value"].encode("utf8")
                 newPDDI["evidenceRole"] = evMode
                 obj =  resultset["results"]["bindings"][i]["object"]["value"].encode("utf8")
                 newPDDI["object"] = obj.replace(u"https://dbmi-icode-01.dbmi.pitt.edu/dikb/resource/Drugs/",u"").upper().encode("utf8")
                 precip = resultset["results"]["bindings"][i]["precip"]["value"].encode("utf8")
                 newPDDI["precip"] = precip.replace(u"https://dbmi-icode-01.dbmi.pitt.edu/dikb/resource/Drugs/",u"").upper().encode("utf8")
                 newPDDI["numericVal"] = resultset["results"]["bindings"][i]["numericVal"]["value"].encode("utf8")
                 newPDDI["contVal"] = resultset["results"]["bindings"][i]["contVal"]["value"].encode("utf8")
                 newPDDI["evidenceSource"] = resultset["results"]["bindings"][i]["evSource"]["value"].encode("utf8")
                 newPDDI["evidenceType"] = resultset["results"]["bindings"][i]["evType"]["value"].encode("utf8")
                 newPDDI["evidenceVal"] = resultset["results"]["bindings"][i]["evidenceVal"]["value"].encode("utf8")

                 if resultset["results"]["bindings"][i].has_key("content"):
                     newPDDI["evidenceStatement"] = resultset["results"]["bindings"][i]["content"]["value"].encode("utf8")
                     newPDDI["objectDose"] = resultset["results"]["bindings"][i]["objectDose"]["value"].encode("utf8")
                     newPDDI["precipDose"] = resultset["results"]["bindings"][i]["precipDose"]["value"].encode("utf8")
                     newPDDI["numOfSubjects"] = resultset["results"]["bindings"][i]["numOfSubjects"]["value"].encode("utf8")

             newPDDI["label"] = resultset["results"]["bindings"][i]["label"]["value"].encode("utf8")

             pddiDictL.append(newPDDI)
    return pddiDictL


def queryAssertion(assertType, evMode, num):

    evidenceMode = None
    if evMode is "support":
        evidenceMode = "citesAsSupportingEvidence"
    elif evMode is "refute":
        evidenceMode = "citesAsRefutingEvidence"

    pddiDictL = []

    sparql_service = "https://dbmi-icode-01.dbmi.pitt.edu/dikb/sparql"

    if assertType == "does_not_inhibit":
        query_string = doseNotInhibitQry(evidenceMode, num)
    else:
        query_string = assertionQry(assertType, evidenceMode, num)

    print "[INFO] assertion type - %s \n  query_string: %s" % (assertType, query_string)
    json_string = query(query_string, sparql_service)
    
    resultset=json.loads(json_string)
    print "[INFO] Number of results: " + str(len(resultset["results"]["bindings"]))

    if len(resultset["results"]["bindings"]) == 0:
        print "INFO: No result!"
    else:
        #print json.dumps(resultset,indent=1)
        for i in range(0, len(resultset["results"]["bindings"])):

             newPDDI = getAssertionDict()

             newPDDI["researchStatementLabel"] = resultset["results"]["bindings"][i]["researchStatementLabel"]["value"].encode("utf8")

             if assertType in ["substrate_of", "inhibits", "is_not_substrate_of"]:
                 newPDDI["assertType"] = assertType
             elif "does_not_inhibit" in newPDDI["researchStatementLabel"]:
                 newPDDI["assertType"] = "does_not_inhibit"
             else:
                 newPDDI["assertType"] = "None"
             
             newPDDI["valueURI"] = resultset["results"]["bindings"][i]["valueURI"]["value"].encode("utf8")
             newPDDI["objectURI"] = resultset["results"]["bindings"][i]["objectURI"]["value"].encode("utf8")
             newPDDI["homepage"] = resultset["results"]["bindings"][i]["homepage"]["value"].encode("utf8")

             if resultset["results"]["bindings"][i].has_key("whoAnnotated"):
                 newPDDI["whoAnnotated"] = resultset["results"]["bindings"][i]["whoAnnotated"]["value"].encode("utf8")

             if resultset["results"]["bindings"][i].has_key("dateAnnotated"):
                 newPDDI["dateAnnotated"] = resultset["results"]["bindings"][i]["dateAnnotated"]["value"].encode("utf8")

             if resultset["results"]["bindings"][i].has_key("evidence"):
                 newPDDI["evidence"] = resultset["results"]["bindings"][i]["evidence"]["value"].encode("utf8")
                 newPDDI["evidenceRole"] = evMode
                 newPDDI["evidenceSource"] = resultset["results"]["bindings"][i]["evSource"]["value"].encode("utf8")
                 newPDDI["evidenceType"] = resultset["results"]["bindings"][i]["evType"]["value"].encode("utf8")

                 if resultset["results"]["bindings"][i].has_key("content"):
                     newPDDI["evidenceStatement"] = resultset["results"]["bindings"][i]["content"]["value"].encode("utf8")
             #newPDDI["label"] = resultset["results"]["bindings"][i]["label"]["value"].encode("utf8")


             ## handle biodirectional relationships for substrate_of and inhibits ##

             # if assertType in ["does_not_inhibit", "is_not_substrate_of"]:

             #     if assertType == "does_not_inhibit":
             #         newPDDI["assertType"] = "inhibits"
             #         newPDDI["researchStatementLabel"] = newPDDI["researchStatementLabel"].replace("does_not_inhibit","inhibits")
             #         newPDDI["homepage"] = newPDDI["homepage"].replace("does_not_inhibit","inhibits")
             #     else:
             #         newPDDI["assertType"] = "substrate_of"
             #         newPDDI["researchStatementLabel"] = newPDDI["researchStatementLabel"].replace("is_not_substrate_of","substrate_of")
             #         newPDDI["homepage"] = newPDDI["homepage"].replace("is_not_substrate_of","substrate_of")
                     

             #    if evMode == "support":
             #        newPDDI["evidenceRole"] = "refute"
             #    elif evMode == "refute":
             #        newPDDI["evidenceRole"] = "support"

             pddiDictL.append(newPDDI)

    return pddiDictL


## print increaseAUC to csv
## inputs: list, filepath + filename, write wb or a
def printIncreaseAuc(increaseAUCDictL, filepath, writeType):

    with open(filepath, writeType) as tsvfile:
        writer = csv.DictWriter(tsvfile, delimiter='\t', fieldnames=["researchStatementLabel", "assertType", "objectURI","valueURI","label","homepage","source","dateAnnotated","whoAnnotated", "evidence", "evidenceVal", "evidenceRole","object","precip","numericVal","evidenceVal","contVal","evidenceSource","evidenceType","evidenceStatement","objectDose", "precipDose", "numOfSubjects"])
        if writeType is "wb":
            writer.writeheader()

        for line in increaseAUCDictL:
            writer.writerow(line)


def printAssertionByType(assertionDictL, filepath, writeType):
    with open(filepath, writeType) as tsvfile:
        writer = csv.DictWriter(tsvfile, delimiter='\t', fieldnames=["researchStatementLabel","assertType", "objectURI","valueURI","label","homepage","source", "dateAnnotated","whoAnnotated", "evidence", "evidenceRole","evidenceSource","evidenceType","evidenceStatement"])
        if writeType is "wb":
            writer.writeheader()

        for line in assertionDictL:
            writer.writerow(line)


if __name__ == "__main__":

    num = 1000

    ###### increase_auc ######
    
    aucSupportL = queryIncreaseAuc("support", num)
    aucRefuteL = queryIncreaseAuc("refute", num)
    filepath = "../../data/dikb-pddis/dikb-increaseAUC-ddis.tsv"
    printIncreaseAuc(aucSupportL + aucRefuteL, filepath, "wb")

    # ###### substrate_of ######

    filepath1 = "../../data/dikb-pddis/dikb-assertion-ddis.tsv"
    substrateOfSupportL = queryAssertion("substrate_of", "support", num)
    substrateOfRefuteL = queryAssertion("substrate_of", "refute", num)
    printAssertionByType(substrateOfSupportL + substrateOfRefuteL, filepath1, "wb")

    # ###### is_not_substrate_of ######

    # isNotSubstrateOfSupportL = queryAssertion("is_not_substrate_of", "support", num)
    # isNotSubstrateOfRefuteL = queryAssertion("is_not_substrate_of", "refute", num)
    # printAssertionByType(isNotSubstrateOfSupportL + isNotSubstrateOfRefuteL, filepath1, "a")

    # ###### inhibits ######

    inhibitsSupportL = queryAssertion("inhibits", "support", num)
    inhibitsRefuteL = queryAssertion("inhibits", "refute", num)
    printAssertionByType(inhibitsSupportL + inhibitsRefuteL, filepath1, "a")

    # ###### dose_not_inhibit ######

    # doesNotInhibitsSupportL = queryAssertion("does_not_inhibit", "support", num)
    # doesNotInhibitsRefuteL = queryAssertion("does_not_inhibit", "refute", num)
    # printAssertionByType(doesNotInhibitsSupportL + doesNotInhibitsRefuteL, filepath1, "a")


