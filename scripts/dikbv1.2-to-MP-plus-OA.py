### dikbv1.2-to-MP-plus-OA.py
##
## TRANSLATE PDDI ASSERTIONS AND EVIDENCE IN THE DIKB TO MICROPUBLICATION LINKED TO  OPEN DATA ANNOTATION
## 
## The Drug Interaction Knowledge Base (DIKB) is (C) Copyright 2005 - 2015 by
## Richard Boyce

## Original Authors:
##   Richard Boyce, Yifan Ning, Jodi Schneider, Tim Clark, Paolo Ciccarese, Paul Groth

## This code is licensed under Apache License Version 2.0, January
## 2004. Please see the license in the root folder of this project

import sys
sys.path = sys.path + ['.']

import re, codecs, uuid, datetime
import json
import urllib2
import urllib
import traceback
import csv
import difflib


## import Sparql-related
from SPARQLWrapper import SPARQLWrapper, JSON

## import RDF related
from rdflib import Graph, BNode, Literal, Namespace, URIRef, RDF, RDFS, XSD

## to retrieve from PubMed
from Bio import Entrez

#reload(sys);
#sys.setdefaultencoding("utf8")

DRUGBANK_CHEBI = "../data/drugbank-to-chebi-06232015.txt"


################################################################################
# Globals
################################################################################
PRE_POST_CHARS=50
mp_list = []

annotationSetCntr = 1
annotationItemCntr = 1
annotationDataCntr = 1
annotationClaimCntr = 1
annotationMaterialCntr = 1
annotationMethodCntr = 1
annotationStatementCntr = 1



## set up RDF graph
# identify namespaces for other ontologies to be used                                                                                    
dcterms = Namespace("http://purl.org/dc/terms/")
pav = Namespace("http://purl.org/pav")
dctypes = Namespace("http://purl.org/dc/dcmitype/")
dailymed = Namespace('http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/vocab/resource/')
sio = Namespace('http://semanticscience.org/resource/')
oa = Namespace('http://www.w3.org/ns/oa#')
aoOld = Namespace('http://purl.org/ao/core/') # needed for AnnotationSet and item until the equivalent is in Open Data Annotation
cnt = Namespace('http://www.w3.org/2011/content#')
gcds = Namespace('http://www.genomic-cds.org/ont/genomic-cds.owl#')

siocns = Namespace('http://rdfs.org/sioc/ns#')
swande = Namespace('http://purl.org/swan/1.2/discourse-elements#')
dikbD2R = Namespace('http://dbmi-icode-01.dbmi.pitt.edu/dikb/vocab/resource/')
linkedspls = Namespace('file:///home/rdb20/Downloads/d2rq-0.8.1/linkedSPLs-dump.nt#structuredProductLabelMetadata/')
poc = Namespace('http://purl.org/net/nlprepository/spl-ddi-annotation-poc#')
ncbit = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
dikbEvidence = Namespace('http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#')
mp = Namespace('http://purl.org/mp/') # namespace for micropublication
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')



################################################################################
# Functions
################################################################################

## correctly retrieve PubMed abstracts using PMIDs
def retrieveByEUtils(pmid, limit=None):
    rslt_D = {}

    Entrez.email = 'pharmgx@gmail.com'
    rec_abs = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", Retmode="text")
    data = rec_abs.read()

    return data


def getDrugbankIdChEBIMappingD(fileInput):
    drugbankChEBID = {}
    with open(fileInput, "r") as inputMapping:
        lines = inputMapping.readlines()
        for line in lines:
            array = line.split("\t")
            drugbankId = array[2].replace("http://www.drugbank.ca/drugs/","")
            drugbankChEBID[drugbankId] = array[0]
    return drugbankChEBID


def getSPLSectionsSparql(spl, sparql):
    splUri = "http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/resource/structuredProductLabelMetadata/" + spl.strip()

    qry = '''
PREFIX dailymed: <http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/vocab/resource/>

SELECT 
?fullName ?genericMedicine ?adverseReactions ?boxedWarning ?clinicalPharmacology ?clinicalStudies ?contraindications ?description ?dosageAndAdministration ?drugInteractions ?indicationsAndUsage ?patientMedicationInformation ?informationForPatients ?precautions ?useInSpecificPopulations ?warningsAndPrecautions ?warnings

WHERE { 
    OPTIONAL { <%s> dailymed:fullName   ?fullName}
    OPTIONAL { <%s> dailymed:genericName   ?genericMedicine}
    OPTIONAL { <%s> dailymed:adverseReactions   ?adverseReactions }
    OPTIONAL { <%s> dailymed:boxedWarning   ?boxedWarning }
    OPTIONAL { <%s> dailymed:clinicalPharmacology   ?clinicalPharmacology }
    OPTIONAL { <%s> dailymed:clinicalStudies   ?clinicalStudies }
    OPTIONAL { <%s> dailymed:contraindications   ?contraindications }
    OPTIONAL { <%s> dailymed:description   ?description }
    OPTIONAL { <%s> dailymed:dosageAndAdministration   ?dosageAndAdministration }
    OPTIONAL { <%s> dailymed:drugInteractions   ?drugInteractions }
    OPTIONAL { <%s> dailymed:indicationsAndUsage   ?indicationsAndUsage }
    OPTIONAL { <%s> dailymed:patientMedicationInformation   ?patientMedicationInformation }
    OPTIONAL { <%s> dailymed:informationForPatients   ?informationForPatients }
    OPTIONAL { <%s> dailymed:precautions   ?precautions }
    OPTIONAL { <%s> dailymed:useInSpecificPopulations   ?useInSpecificPopulations }
    OPTIONAL { <%s> dailymed:warningsAndPrecautions   ?warningsAndPrecautions }
    OPTIONAL { <%s> dailymed:warnings   ?warnings }
}
''' % (splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri,splUri)

    #print "QUERY: %s" % qry

    sparql.setQuery(qry)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print "%s" % results

    if len(results["results"]["bindings"]) == 0:
        print "ERROR: no results from query"
        return {}

    secD = {
        "fullName":None,
        "genericMedicine":None,
        "adverseReactions":None,
        "boxedWarning":None,
        "clinicalPharmacology":None,
        "clinicalStudies":None,
        "contraindications":None,
        "description":None,
        "dosageAndAdministration":None,
        "drugInteractions":None,
        "indicationsAndUsage":None,
        "patientMedicationInformation":None,
        "informationForPatients":None,
        "precautions":None,
        "useInSpecificPopulations":None,
        "warningsAndPrecautions":None,
        "warnings":None
        }

    for k in secD.keys():
        if results["results"]["bindings"][0].has_key(k):
            secD[k] = unicode(results["results"]["bindings"][0][k]["value"])

    return secD



def addOAItem(graph, item):
    prefix = "None"
    postfix = "None"

    ## parse oa:selector in OA, extract the 'exact' drug interaction statement
    index_quoted = item["evidenceStatement"].find('Quote') 

    if index_quoted > 0:
        exact=item["evidenceStatement"][index_quoted:]
    else:
        exact= item["evidenceStatement"]
        rgx = re.compile(u"quote ?:", re.I)
        exact = rgx.sub(u"",exact)

    source = "None"
    if "pubmed" in item["evidenceSource"]:
        source = item["evidenceSource"]
    else:
        if "resource/structuredProductLabelMetadata/" in item["evidenceSource"]:
            setid = item["evidenceSource"].replace("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/resource/structuredProductLabelMetadata/","")
        if "page/structuredProductLabelMetadata/" in item["evidenceSource"]:
            setid = item["evidenceSource"].replace("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/page/structuredProductLabelMetadata/","")
            source = u"http://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=%s" % unicode(setid)

    global annotationItemCntr
    currentAnnotItem = "ddi-spl-annotation-item-%s" % annotationItemCntr
    annotationItemCntr += 1
    
    graph.add((poc[currentAnnotItem], RDF.type, oa["Annotation"]))
    graph.add((poc[currentAnnotItem], oa["annotatedAt"], Literal(item["dateAnnotated"], datatype=XSD.String)))
    graph.add((poc[currentAnnotItem], oa["annotatedBy"], Literal(item["whoAnnotated"], datatype=XSD.String))) 
    graph.add((poc[currentAnnotItem], oa["motivatedBy"], oa["tagging"]))
    
    currentAnnotTargetUuid = URIRef(u"urn:uuid:%s" % uuid.uuid4())
    textConstraintUuid = URIRef(u"urn:uuid:%s" % uuid.uuid1())

    graph.add((poc[currentAnnotItem], oa["hasTarget"], currentAnnotTargetUuid))
    graph.add((currentAnnotTargetUuid, RDF.type, oa["SpecificResource"]))
    graph.add((currentAnnotTargetUuid, oa["hasSource"], Literal(source, datatype=XSD.String)))

    graph.add((currentAnnotTargetUuid, oa["hasSelector"], textConstraintUuid))
    graph.add((textConstraintUuid, RDF.type, oa["TextQuoteSelector"]))
    graph.add((textConstraintUuid, oa["exact"], Literal(exact, datatype=XSD.String)))
    graph.add((textConstraintUuid, oa["prefix"], Literal(prefix, datatype=XSD.String)))
    graph.add((textConstraintUuid, oa["postfix"], Literal(postfix, datatype=XSD.String))) 

    return currentAnnotItem


def addNonTraceable(graph, item, currentAnnotationClaim):

    ##### OA - EACH SPL HAS A SET OF ANNOTATIONS, EACH WITH A TARGET AND BODY #####
    oaItem = addOAItem(graph, item)

    ##### OA - Non traceable statement supports mp:Claim #####

    #Statement
    global annotationStatementCntr
    currentAnnotationStatement = "ddi-spl-annotation-statement-%s" % annotationStatementCntr
    annotationStatementCntr += 1

    graph.add((poc[currentAnnotationStatement], RDF.type, dikbEvidence["Non_traceable_Drug_Label_Statement"]))
    graph.add((dikbEvidence["Non_traceable_Drug_Label_Statement"], RDFS.subClassOf, mp["Statement"]))

    # Relationships
    graph.add((poc[oaItem], oa["hasBody"], poc[currentAnnotationStatement]))
    graph.add((poc[currentAnnotationStatement], mp["supports"], poc[currentAnnotationClaim]))


def addAssertion(graph, item, currentAnnotationClaim):

    ##### OA - EACH SPL HAS A SET OF ANNOTATIONS, EACH WITH A TARGET AND BODY #####
    oaItem = addOAItem(graph, item)

    # Claim : is a research statement label qualified by assertion URI
    # global annotationClaimCntr 
    # currentAnnotationClaim = "ddi-spl-annotation-claim-%s" % annotationClaimCntr
    # annotationClaimCntr += 1
    # graph.add((poc[currentAnnotationClaim],RDF.type, mp["Claim"]))

    if item['researchStatementLabel']:
        graph.add((poc[currentAnnotationClaim], RDFS.label, Literal(item["researchStatementLabel"])))

    if item['researchStatement']:
        graph.add((poc[currentAnnotationClaim], mp["qualifiedBy"], URIRef(item["researchStatement"])))
        graph.add((URIRef(item["researchStatement"]), RDF.type, mp["SemanticQualifier"]))
    else:
        graph.add((poc[currentAnnotationClaim], mp["qualifiedBy"], Literal("stubbed out"))) 


    # Method : used in data to supports statement
    global annotationMethodCntr
    currentAnnotationMethod = "ddi-spl-annotation-method-%s" % annotationMethodCntr
    annotationMethodCntr += 1    
    graph.add((poc[currentAnnotationMethod], RDF.type, URIRef(item["evidenceType"])))
    graph.add((URIRef(item["evidenceType"]), RDFS.subClassOf, mp["Method"]))

    # Data : supports statement
    global annotationDataCntr
    currentAnnotationData = "ddi-spl-annotation-data-%s" % annotationDataCntr
    annotationDataCntr += 1
    graph.add((poc[currentAnnotationData], RDF.type, URIRef(item["evidenceType"]+"_Data")))
    graph.add((URIRef(item["evidenceType"]), RDFS.subClassOf, mp["Data"]))

    # Material
    global annotationMaterialCntr
    currentAnnotationMaterial = "ddi-spl-annotation-material-%s" % annotationMaterialCntr
    annotationMaterialCntr += 1
    graph.add((poc[currentAnnotationMaterial], RDF.type, URIRef(item["evidenceType"]+"_Material"))) 
    graph.add((URIRef(item["evidenceType"]+"_Material"), RDFS.subClassOf, mp["Material"])) 


    ## increase AUC have PKDDI material info

    if item["assertType"] is "increase_auc":
 
        graph.add((poc[currentAnnotationMaterial], RDFS.label, Literal("%s (object) - %s (precipitant)" % (item["object"], item["precip"]))))

        graph.add((poc[currentAnnotationMaterial], dikbD2R['ObjectDrugOfInteraction'], URIRef(item["objectURI"])))
        graph.add((poc[currentAnnotationMaterial], dikbD2R['PrecipitantDrugOfInteraction'], URIRef(item["valueURI"])))
        graph.add((poc[currentAnnotationMaterial], dikbD2R['objectDose'], Literal(item["objectDose"])))
        graph.add((poc[currentAnnotationMaterial], dikbD2R['precipitantDose'], Literal(item["precipDose"])))
        graph.add((poc[currentAnnotationMaterial], dikbD2R['numOfSubjects'], Literal(item["numOfSubjects"])))

        if item["numericVal"]:
            graph.add((poc[currentAnnotationData], dikbD2R["increases_auc"], Literal(item["numericVal"])))
        else:
            graph.add((poc[currentAnnotationData], dikbD2R["increases_auc"], Literal("stubbed out")))

    # Relationships
    graph.add((poc[currentAnnotationMaterial], mp["usedIn"], poc[currentAnnotationMethod]))
    graph.add((poc[currentAnnotationMethod], mp["supports"], poc[currentAnnotationData]))
    graph.add((poc[currentAnnotationData], mp["supports"], poc[currentAnnotationClaim]))
    graph.add((poc[oaItem], oa["hasBody"], poc[currentAnnotationData]))

    graph.add((poc[oaItem], oa["hasBody"], poc[currentAnnotationMethod]))


## set up SPARQL for acquiring the SPL sections
#lsplsparql = SPARQLWrapper("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/sparql")
lsplsparql = SPARQLWrapper("http://dbmi-icode-01.dbmi.pitt.edu:8080/sparql")


def initialGraph(graph):

    graph.namespace_manager.reset()
    graph.namespace_manager.bind("dcterms", "http://purl.org/dc/terms/")
    graph.namespace_manager.bind("pav", "http://purl.org/pav");
    graph.namespace_manager.bind("dctypes", "http://purl.org/dc/dcmitype/")
    graph.namespace_manager.bind('dailymed','http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/vocab/resource/')
    graph.namespace_manager.bind('sio', 'http://semanticscience.org/resource/')
    graph.namespace_manager.bind('oa', 'http://www.w3.org/ns/oa#')
    graph.namespace_manager.bind('aoOld', 'http://purl.org/ao/core/') # needed for AnnotationSet and item until the equivalent is in Open Data Annotation
    graph.namespace_manager.bind('cnt', 'http://www.w3.org/2011/content#')
    graph.namespace_manager.bind('gcds','http://www.genomic-cds.org/ont/genomic-cds.owl#')

    graph.namespace_manager.bind('siocns','http://rdfs.org/sioc/ns#')
    graph.namespace_manager.bind('swande','http://purl.org/swan/1.2/discourse-elements#')
    graph.namespace_manager.bind('dikbD2R','http://dbmi-icode-01.dbmi.pitt.edu/dikb/vocab/resource/')

    graph.namespace_manager.bind('linkedspls','file:///home/rdb20/Downloads/d2rq-0.8.1/linkedSPLs-dump.nt#structuredProductLabelMetadata/')
    graph.namespace_manager.bind('poc','http://purl.org/net/nlprepository/spl-ddi-annotation-poc#')
    graph.namespace_manager.bind('ncbit','http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
    graph.namespace_manager.bind('dikbEvidence','http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#')
    graph.namespace_manager.bind('mp','http://purl.org/mp/')
    graph.namespace_manager.bind('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')


    ### open annotation ontology properties and classes
    graph.add((dctypes["Collection"], RDFS.label, Literal("Collection"))) # Used in lieau of the AnnotationSet https://code.google.com/p/annotation-ontology/wiki/AnnotationSet
    graph.add((dctypes["Collection"], dcterms["description"], Literal("A collection is described as a group; its parts may also be separately described. See http://dublincore.org/documents/dcmi-type-vocabulary/#H7")))

    graph.add((oa["Annotation"], RDFS.label, Literal("Annotation")))
    graph.add((oa["Annotation"], dcterms["description"], Literal("Typically an Annotation has a single Body (oa:hasBody), which is the comment or other descriptive resource, and a single Target (oa:hasTarget) that the Body is somehow 'about'. The Body provides the information which is annotating the Target. See  http://www.w3.org/ns/oa#Annotation")))

    graph.add((oa["annotatedBy"], RDFS.label, Literal("annotatedBy")))
    graph.add((oa["annotatedBy"], RDF.type, oa["objectproperties"]))

    graph.add((oa["annotatedAt"], RDFS.label, Literal("annotatedAt")))
    graph.add((oa["annotatedAt"], RDF.type, oa["dataproperties"]))

    graph.add((oa["TextQuoteSelector"], RDFS.label, Literal("TextQuoteSelector")))
    graph.add((oa["TextQuoteSelector"], dcterms["description"], Literal("A Selector that describes a textual segment by means of quoting it, plus passages before or after it. See http://www.w3.org/ns/oa#TextQuoteSelector")))

    graph.add((oa["hasSelector"], RDFS.label, Literal("hasSelector")))
    graph.add((oa["hasSelector"], dcterms["description"], Literal("The relationship between a oa:SpecificResource and a oa:Selector. See http://www.w3.org/ns/oa#hasSelector")))

    # these predicates are specific to SPL annotation
    graph.add((sio["SIO_000628"], RDFS.label, Literal("refers to")))
    graph.add((sio["SIO_000628"], dcterms["description"], Literal("refers to is a relation between one entity and the entity that it makes reference to.")))

    graph.add((sio["SIO_000563"], RDFS.label, Literal("describes")))
    graph.add((sio["SIO_000563"], dcterms["description"], Literal("describes is a relation between one entity and another entity that it provides a description (detailed account of)")))

    graph.add((sio["SIO_000338"], RDFS.label, Literal("specifies")))
    graph.add((sio["SIO_000338"], dcterms["description"], Literal("A relation between an information content entity and a product that it (directly/indirectly) specifies")))




def createGraph(graph, dataset):

    for item in dataset:   

        if "www4.wiwiss" in item["objectURI"]:
            objectDBId = item["objectURI"].replace("http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugs/","")
            if drugbankIdChEBID.has_key(objectDBId):
                item["objectURI"] = drugbankIdChEBID[objectDBId]
            else:
                continue

        if "www4.wiwiss" in item["valueURI"]:
            valueDBId = item["valueURI"].replace("http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugs/","")

            if drugbankIdChEBID.has_key(valueDBId):
                item["valueURI"] = drugbankIdChEBID[valueDBId]
            else:
                continue


        ###################################################################
        # MP - Claim (label, subject, predicate, object)
        ###################################################################

        # Claim : is a research statement label qualified by assertion URI
        if item['researchStatementLabel']:

            global annotationClaimCntr 
            currentAnnotationClaim = "ddi-spl-annotation-claim-%s" % (annotationClaimCntr)
            annotationClaimCntr += 1

            graph.add((poc[currentAnnotationClaim],RDF.type, mp["Claim"]))
            graph.add((poc[currentAnnotationClaim], RDFS.label, Literal(item["researchStatementLabel"])))

            if item['researchStatement']:
                graph.add((poc[currentAnnotationClaim], mp["logicalClaim"], URIRef(item["researchStatement"])))
                graph.add((URIRef(item["researchStatement"]), RDF.type, mp["SemanticQualifier"]))

                graph.add((poc[currentAnnotationClaim], rdf["subject"], URIRef(item["objectURI"])))
                graph.add((URIRef(item["objectURI"]), RDF.type, mp["SemanticQualifier"]))

                graph.add((poc[currentAnnotationClaim], rdf["object"], URIRef(item["valueURI"])))
                graph.add((URIRef(item["valueURI"]), RDF.type, mp["SemanticQualifier"]))

                graph.add((poc[currentAnnotationClaim], rdf["predicate"], URIRef(item["assertType"])))
                graph.add((URIRef(item["assertType"]), RDF.type, mp["SemanticQualifier"]))

            else:
                graph.add((poc[currentAnnotationClaim], mp["logicalClaim"], Literal("stubbed out")))

        ###################################################################
        # MP - Evidence (Non traceable, Other evidences)
        ###################################################################

        ## if it's traceble statement
        ## multiple bodies - mp:data, mp:Method, mp:Reference, mp:statement, mp:representation

        if item["evidence"]:

            if item["evidenceType"] != u'http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#Non_traceable_Drug_Label_Statement':
                addAssertion(graph, item, currentAnnotationClaim)

        ## The bodies of non_traceable statement is different
        ## statement typed as 'Non_traceable_Drug_Label_Statement' don't have evidence
            else:
                addNonTraceable(graph, item, currentAnnotationClaim)
        mp_list.append(item)


    ############################# QUYERY VALIDATION ###############################

    print "\n#####################TOTAL ITEMS#####################\n"
    print "Claim: %s | Data: %s | Method: %s | Material: %s \n" % (str(annotationClaimCntr - 1), str(annotationDataCntr - 1), str(annotationMethodCntr - 1), str(annotationMaterialCntr - 1))


def printGraphToCSVRDF(mp_list, OUT_GRAPH, OUT_CSV):
    # display the graph
    f = codecs.open(OUT_GRAPH,"w","utf8")
    #graph.serialize(destination=f,format="xml",encoding="utf8")
    s = graph.serialize(format="xml",encoding="utf8")

    #f.write(graph.serialize(format="xml",encoding="utf8"))
    f.write(unicode(s,errors='replace'))
    #print graph.serialize(format="xml")
    f.close
    graph.close()

    ## write in tsv file
    #try:
    with open(OUT_CSV, 'wb') as tsvfile:
        writer = csv.DictWriter(tsvfile, delimiter='\t', fieldnames=["researchStatement","researchStatementLabel", "assertType", "objectURI","valueURI","label","homepage","source","dateAnnotated","whoAnnotated", "evidence", "evidenceVal", "evidenceRole","object","precip","numericVal","contVal","evidenceSource","evidenceType","evidenceStatement","objectDose", "precipDose", "numOfSubjects"])
        writer.writeheader()
        writer.writerows(mp_list)




############################# MAIN ###############################

if __name__ == "__main__":

    OUT_GRAPH = "../data/initial-dikb-mp-oa.xml"
    OUT_CSV = "../data/processed-dikb-ddis.tsv"

    # PDDIs from DIKB
    dataset_increaseAUC = csv.DictReader(open("../data/dikb-pddis/dikb-increaseAUC-ddis.tsv","rb"), delimiter='\t')
    dataset_assertion = csv.DictReader(open("../data/dikb-pddis/dikb-assertion-ddis.tsv","rb"), delimiter='\t')

    drugbankIdChEBID = getDrugbankIdChEBIMappingD(DRUGBANK_CHEBI)

    graph = Graph()
    initialGraph(graph)

    createGraph(graph, dataset_increaseAUC)
    createGraph(graph, dataset_assertion)

    printGraphToCSVRDF(mp_list, OUT_GRAPH, OUT_CSV)



################################# trash #################################3

## parse to get prefix and postfix based on exact and index_exact
    # if index_exact >= 0:

    #     if index_exact < PRE_POST_CHARS:
    #         prefix = section_text[0:index_exact]
    #     else: 
    #         prefix = section_text[int(index_exact - PRE_POST_CHARS):int(index_exact-1)]

    #     if index_exact + len(exact) + PRE_POST_CHARS > len(section_text):
    #         postfix = section_text[index_exact+len(exact):]
    #     else:
    #         postfix = section_text[index_exact+len(exact):index_exact+len(exact)+PRE_POST_CHARS]
    # else:
    #     prefix = ""
    #     postfix = ""
		      	  
    #print u"EXACT: %s" % exact
	
    #print u"PRE: %s" % prefix
	
    #print u"POST: %s" % postfix

##--------------------------------------------------

    # contentD = {}

    # try:
    #     contentD = getSPLSectionsSparql(setid, lsplsparql)

    # except urllib2.HTTPError:
    #     print "problem in retrieving SPL contents"

    # if contentD == {}:
    #     continue

    # print "get spl resultsets from sparql"
    # section_text = ""
    # index_exact = -1
    # max_match = 0

    # for k,v in contentD.iteritems(): 
    #     if not v:
    #         continue

    #     s = difflib.SequenceMatcher(None, exact, v)
    #     match_tuples = s.find_longest_match(0, len(exact),0 , len(v))

    #     if match_tuples[2] > max_match :
    #         max_match = match_tuples[2]
    #         index_exact = match_tuples[1]
    #         section_text = v


#----------------------------------------------------
    #print "GETTING SECTIONS FOR PUBMED: %s" % item["evidenceSource"]

   ## TODO: handle those items from the scientific literature  - i.e., sources from PubMed. Use eutils to retrieve the abstract                    

    # section_text = retrieveByEUtils(pmid)
    # print str("Abstract:"+section_text)
    # match exact in abstract to get prefix and postfix
    # index_exact = section_text.lower().find(exact.lower())
