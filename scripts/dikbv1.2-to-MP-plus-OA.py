### dikbv1.2-to-MP-plus-OA.py
##
## TRANSLATE PDDI ASSERTIONS AND EVIDENCE IN THE DIKB TO MICROPUBLICATION LINKED TO  OPEN DATA ANNOTATION
## 
## The Drug Interaction Knowledge Base (DIKB) is (C) Copyright 2005 - 2015 by
## Richard Boyce

## Original Authors:
##   Richard Boyce, Yifan Ning, Jodi Schneider, Tim Clark, Paolo Ciccarese

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
from rdflib import Graph, BNode, Literal, Namespace, URIRef, RDF, RDFS

## to retrieve from PubMed
from Bio import Entrez

#reload(sys);
#sys.setdefaultencoding("utf8")


################################################################################
# Globals
################################################################################
PRE_POST_CHARS=50
OUT_FILE="../data/initial-dikb-mp-oa-Aug2014.xml"
#OUT_FILE="../data/initial-dikb-mp-oa-Aug2014-test.xml"


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


## set up SPARQL for acquiring the SPL sections
#lsplsparql = SPARQLWrapper("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/sparql")
lsplsparql = SPARQLWrapper("http://dbmi-icode-01.dbmi.pitt.edu:8080/sparql")

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



graph = Graph()

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

graph.add((oa["SpecificResource"], RDFS.label, Literal("SpecificResource")))
graph.add((oa["SpecificResource"], dcterms["description"], Literal("A resource identifies part of another Source resource, a particular representation of a resource, a resource with styling hints for renders, or any combination of these. See http://www.w3.org/ns/oa#SpecificResource")))

# these predicates are specific to SPL annotation
graph.add((sio["SIO_000628"], RDFS.label, Literal("refers to")))
graph.add((sio["SIO_000628"], dcterms["description"], Literal("refers to is a relation between one entity and the entity that it makes reference to.")))

graph.add((sio["SIO_000563"], RDFS.label, Literal("describes")))
graph.add((sio["SIO_000563"], dcterms["description"], Literal("describes is a relation between one entity and another entity that it provides a description (detailed account of)")))

graph.add((sio["SIO_000338"], RDFS.label, Literal("specifies")))
graph.add((sio["SIO_000338"], dcterms["description"], Literal("A relation between an information content entity and a product that it (directly/indirectly) specifies")))

## PD
graph.add((poc['PharmacodynamicImpact'], RDFS.label, Literal("PharmacodynamicImpact")))
graph.add((poc['PharmacodynamicImpact'], dcterms["description"], Literal("Information on the pharmacodynamic impact of a pharmacogenomic biomarker.")))

graph.add((poc['drug-toxicity-risk-increased'], RDFS.label, Literal("drug-toxicity-risk-increased")))
graph.add((poc['drug-toxicity-risk-increased'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an increased risk of toxicity. ")))

graph.add((poc['drug-toxicity-risk-decreased'], RDFS.label, Literal("drug-toxicity-risk-decreased")))
graph.add((poc['drug-toxicity-risk-decreased'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an decreased risk of toxicity.")))

graph.add((poc['drug-efficacy-increased-from-baseline'], RDFS.label, Literal("drug-efficacy-increased-from-baseline")))
graph.add((poc['drug-efficacy-increased-from-baseline'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an increase in the efficacy of the drug.")))

graph.add((poc['drug-efficacy-decreased-from-baseline'], RDFS.label, Literal("drug-efficacy-decreased-from-baseline")))
graph.add((poc['drug-efficacy-decreased-from-baseline'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in the efficacy of the drug")))

graph.add((poc['influences-drug-response'], RDFS.label, Literal("influences-drug-response")))
graph.add((poc['influences-drug-response'], dcterms["description"], Literal("The pharmacogenomic biomarker influences drug response")))

graph.add((poc['not-important'], RDFS.label, Literal("not-important")))
graph.add((poc['not-important'], dcterms["description"], Literal("The pharmacogenomic biomarker is not associated with a clinically relevant pharmacodynamic effect")))

## PK
graph.add((poc['PharmacokineticImpact'], RDFS.label, Literal("PharmacokineticImpact")))
graph.add((poc['PharmacokineticImpact'], dcterms["description"], Literal("Information on the pharmacokinetic impact of a pharmacogenomic biomarker.")))

graph.add((poc['absorption-increase'], RDFS.label, Literal("absorption-increase")))
graph.add((poc['absorption-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an increase in absorption of the drug. ")))

graph.add((poc['absorption-decrease'], RDFS.label, Literal("absorption-decrease")))
graph.add((poc['absorption-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in absorption of the drug. ")))

graph.add((poc['distribution-increase'], RDFS.label, Literal("distribution-increase")))
graph.add((poc['distribution-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a increase in distribution of the drug")))

graph.add((poc['distribution-decrease'], RDFS.label, Literal("distribution-decrease")))
graph.add((poc['distribution-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in distribution of the drug.")))

graph.add((poc['metabolism-increase'], RDFS.label, Literal("metabolism-increase")))
graph.add((poc['metabolism-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a increase in metabolism of the drug")))

graph.add((poc['metabolism-decrease'], RDFS.label, Literal("metabolism-decrease")))
graph.add((poc['metabolism-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in metabolism of the drug.")))

graph.add((poc['excretion-increase'], RDFS.label, Literal("excretion-increase")))
graph.add((poc['excretion-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a increase in excretion of the drug")))

graph.add((poc['excretion-decrease'], RDFS.label, Literal("excretion-decrease")))
graph.add((poc['excretion-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in excretion of the drug ")))

graph.add((poc['not-important'], RDFS.label, Literal("not-important")))
graph.add((poc['not-important'], dcterms["description"], Literal("The pharmacogenomic biomarker is not associated any clinically relevant pharmacokinetic with respect to the drug. ")))

################################################################################

# OBSERVED DDIs
#data_set = pickle.load( open( "../data/dikb-observed-ddis-test.pickle", "rb" ) )
#data_set = pickle.load( open( "../data/dikb-observed-ddis.pickle", "rb" ) )
data_set = csv.DictReader(open("../data/dikb-observed-ddis.tsv","rb"), delimiter='\t')


annotationSetCntr = 1
annotationItemCntr = 1

annotationDataCntr = 1
annotationMaterialCntr = 1
annotationMethodCntr = 1

annotationEvidenceCntr = 1
annotationReStatementCntr = 1
annotationStatementCntr = 1

splSetIdCache = {} 
source = ""
#graph = Graph()
mp_list = []

## TODO: the code needs to be modified so that the same targets have multiple bodies if that is necessary

#for row in data_set:
#    yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])

for item in data_set:     ## <-------- Use the list of PDDI dictionary instances from the pickle

    
    ## parse oa:selector in OA, extract the 'exact' drug interaction statement
    index_quoted = item["evidenceStatement"].find('Quote') ## TODO: use a regular expression because the quote syntax is sometimes slightly different
    
    if index_quoted > 0:
        exact=item["evidenceStatement"][index_quoted:]
    else:
        #decoded_str = html.decode("windows-1252")
        #encoded_str = decoded_str.encode("utf8")
        #print "test*****"
        exact= item["evidenceStatement"]
        rgx = re.compile(u"quote ?:", re.I)
        exact = rgx.sub(u"",exact)

    
## when evidence froms from dailymed
    if item["evidenceType"] == u'http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#Non_traceable_Drug_Label_Statement':

        if "resource/structuredProductLabelMetadata/" in item["evidenceSource"]:
            setid = item["evidenceSource"].replace("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/resource/structuredProductLabelMetadata/","")
        if "page/structuredProductLabelMetadata/" in item["evidenceSource"]:
            setid = item["evidenceSource"].replace("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/page/structuredProductLabelMetadata/","")


        if setid not in splSetIdCache.keys():
# this is what is indicated by "ex:" in the diagram, a resource with a unique id. I recall that the convention is used in the Open Data Annotation specification too         
            currentAnnotSet = 'ddi-spl-annotation-set-%s' % annotationSetCntr 
        else:
            currentAnnotSet = splSetIdCache[setid]         

            splSetIdCache[setid] = currentAnnotSet
        annotationSetCntr += 1
        
        #print "SETID:" + setid
        source = u"http://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=%s" % unicode(setid)

        #print source + "|"
        print "GETTING SECTIONS FOR DAILYMED: %s" % source
        
        contentD = {}

        try:
            contentD = getSPLSectionsSparql(setid, lsplsparql)
            
        except urllib2.HTTPError:
            print "problem in retrieving SPL contents"
            #print "There is a problem retreiving the SPL content for setid %s. %s" % (setid, urllib2.HTTPError)

        if contentD == {}:
            continue
            
        print "get spl resultsets from sparql"
        section_text = ""
        index_exact = -1
        max_match = 0
    
        for k,v in contentD.iteritems(): 
            if not v:
                continue

            s = difflib.SequenceMatcher(None, exact, v)
            match_tuples = s.find_longest_match(0, len(exact),0 , len(v))
        
            if match_tuples[2] > max_match :
                max_match = match_tuples[2]
                index_exact = match_tuples[1]
                section_text = v
        
                #print max_match
            #print "index_exact - dailymed: " + str(index_exact)



## when evidence forms from pubmed
    else:
        currentAnnotSet = 'ddi-spl-annotation-set-%s' % annotationSetCntr
        annotationSetCntr += 1 
        pmid = item["evidenceSource"].replace("http://www.ncbi.nlm.nih.gov/pubmed/","")
        srouce = unicode(item["evidenceSource"])


       ## TODO: handle those items from the scientific literature  - i.e., sources from PubMed. Use eutils to retrieve the abstract                    
        print "GETTING SECTIONS FOR PUBMED: %s" % item["evidenceSource"]

        section_text = retrieveByEUtils(pmid)
        #print str("Abstract:"+section_text)

        # match exact in abstract to get prefix and postfix
        index_exact = section_text.find(exact)

            
## parse to get prefix and postfix based on exact and index_exact
    if index_exact >= 0:

        if index_exact < PRE_POST_CHARS:
            prefix = section_text[0:index_exact]
        else: 
            prefix = section_text[int(index_exact - PRE_POST_CHARS):int(index_exact-1)]

        if index_exact + len(exact) + PRE_POST_CHARS > len(section_text):
            postfix = section_text[index_exact+len(exact):]
        else:
            postfix = section_text[index_exact+len(exact):index_exact+len(exact)+PRE_POST_CHARS]
    else:
        prefix = ""
        postfix = ""
		      	  
    #print u"EXACT: %s" % exact
	
    print u"PRE: %s" % prefix
	
    print u"POST: %s" % postfix


##### create RDF graph begins, based on OA and MicroPublications Standards        

    ###################################################################
    ### EACH SPL HAS A SET OF ANNOTATIONS, EACH WITH A TARGET AND BODY 
    ###################################################################

    currentAnnotItem = "ddi-spl-annotation-item-%s" % annotationItemCntr
    annotationItemCntr += 1

    graph.add((poc[currentAnnotSet], aoOld["item"], poc[currentAnnotItem])) 
    
    graph.add((poc[currentAnnotItem], RDF.type, oa["Annotation"]))

    graph.add((poc[currentAnnotItem], oa["annotatedAt"], Literal(item["dateAnnotated"])))
    graph.add((poc[currentAnnotItem], oa["annotatedBy"], Literal(item["whoAnnotated"]))) 
# TODO: add 'boycer' to the TRIADS graph and change this annotatedBy to use #boycer
    graph.add((poc[currentAnnotItem], oa["motivatedBy"], oa["tagging"]))
    
### SPECIFY THE TARGET OF THE ANNOTATION - FOR THIS PROJECT, TARGETS ARE ONE OR MORE PORTIONS OF TEXT FROM A GIVEN SPL
    currentAnnotTargetUuid = URIRef(u"urn:uuid:%s" % uuid.uuid4())
    textConstraintUuid = URIRef(u"urn:uuid:%s" % uuid.uuid1())


    graph.add((poc[currentAnnotItem], oa["hasTarget"], currentAnnotTargetUuid))

    #graph.add((currentAnnotTargetUuid, RDF.type, poc["SPLConstrainedTarget"]))
    #graph.add((currentAnnotTargetUuid, RDF.type, oa["ConstrainedTarget"]))
    graph.add((currentAnnotTargetUuid, RDF.type, oa["SpecificResource"]))
    graph.add((currentAnnotTargetUuid, oa["hasSource"], Literal(source)))

    graph.add((currentAnnotTargetUuid, oa["hasSelector"], textConstraintUuid))
    graph.add((textConstraintUuid, RDF.type, oa["TextQuoteSelector"]))
    graph.add((textConstraintUuid, oa["exact"], Literal(exact)))
    graph.add((textConstraintUuid, oa["prefix"], Literal(prefix)))
    graph.add((textConstraintUuid, oa["postfix"], Literal(postfix))) 


    ## SPECIFY THE BODIES OF THE ANNOTATION - FOR THIS PROJECT, EACH
    ##  BODY CONTAINS A DDI SEMANTIC LABEL ASSIGNED TO THE TARGET


    ## if it's traceble statement
    ## multiple bodies - mp:data, mp:Method, mp:Reference, mp:statement, mp:representation

    if item["evidenceType"] != u'http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#Non_traceable_Drug_Label_Statement':

        # Material
        currentAnnotationMaterial = "ddi-spl-annotation-material-%s" % annotationMaterialCntr
        annotationMaterialCntr += 1

        graph.add((poc[currentAnnotationMaterial], RDF.type, mp["Material"])) 
        graph.add((poc[currentAnnotationMaterial], RDFS.label, Literal("%s (object) - %s (precipitant)" % (item["object"], item["precip"]))))
    
        graph.add((poc[currentAnnotationMaterial], sio["SIO_000563"], poc["PharmacokineticImpact"]))#SIO Describes  
        graph.add((poc[currentAnnotationMaterial], poc["PharmacokineticImpact"], poc['metabolism-decrease']))

        graph.add((poc[currentAnnotationMaterial], sio["SIO_000628"], dikbD2R['ObjectDrugOfInteraction']))#SIO refers to
        graph.add((poc[currentAnnotationMaterial], dikbD2R['ObjectDrugOfInteraction'], URIRef(item["objectURI"])))
    
        graph.add((poc[currentAnnotationMaterial], sio["SIO_000628"], dikbD2R['PrecipitantDrugOfInteraction']))
        graph.add((poc[currentAnnotationMaterial], dikbD2R['PrecipitantDrugOfInteraction'], URIRef(item["precipURI"])))

        # Method : used in data to supports statement
        currentAnnotationMethod = "ddi-spl-annotation-method-%s" % annotationMethodCntr
        annotationMethodCntr += 1    
        graph.add((poc[currentAnnotationMethod], RDF.type, Literal(item["evidenceType"])))
        graph.add((poc[currentAnnotationMethod], RDF.type, mp["Method"]))

        # Data : supports statement
        currentAnnotationData = "ddi-spl-annotation-data-%s" % annotationDataCntr
        annotationDataCntr += 1
        graph.add((poc[currentAnnotationData], RDF.type, mp["Data"]))

        if item["ddiPkEffect"]:
            graph.add((poc[currentAnnotationData], dikbD2R["ddiPkEffect"], URIRef(item["ddiPkEffect"])))
        else:
            graph.add((poc[currentAnnotationData], dikbD2R["ddiPkEffect"], Literal("stubbed out")))

            if item["numericVal"]:
                graph.add((poc[currentAnnotationData], dikbD2R["increases_auc"], Literal(item["numericVal"])))
            else:
                graph.add((poc[currentAnnotationData], dikbD2R["increases_auc"], Literal("stubbed out")))

        # Claim : is a research statement label qualified by assertion URI
        if item['researchStatementLabel']:
            graph.add((Literal(item["researchStatementLabel"]),RDF.type, mp["Claim"]))
            graph.add((Literal(item["researchStatementLabel"]), RDF.type, mp["Statement"]))

            if item['researchStatement']:
                graph.add((Literal(item["researchStatementLabel"]), mp["qualifiedBy"], URIRef(item["researchStatement"])))
                graph.add((URIRef(item["researchStatement"]), RDF.type, mp["SemanticQualifier"]))

            else:
                graph.add((Literal(item["researchStatementLabel"]), mp["qualifiedBy"], Literal("stubbed out")))  

        # relationships
        graph.add((poc[currentAnnotationMaterial], mp["usedIn"], poc[currentAnnotationMethod]))
        graph.add((poc[currentAnnotationMethod], mp["supports"], poc[currentAnnotationData]))
    
        if item["researchStatement"]:
            graph.add((poc[currentAnnotationData], mp["supports"], Literal(item["researchStatementLabel"])))

        graph.add((poc[currentAnnotationMethod], mp["represents"], poc[currentAnnotItem]))
        graph.add((poc[currentAnnotationData],mp["represents"], poc[currentAnnotItem]))
 
        graph.add((poc[currentAnnotItem], oa["hasBody"], poc[currentAnnotationMethod]))
        graph.add((poc[currentAnnotItem], oa["hasBody"], poc[currentAnnotationData]))


    ## The bodies of non_traceable statement is different
    ## statement typed as 'Non_traceable_Drug_Label_Statement' don't have evidence to supports or refutes
    else:

        #Statement

        currentAnnotationStatement = "ddi-spl-annotation-statement-%s" % annotationStatementCntr
        annotationStatementCntr += 1

        graph.add((poc[currentAnnotationStatement], RDF.type, dikbEvidence["Non_traceable_Drug_Label_Statement"]))
        graph.add((dikbEvidence["Non_traceable_Drug_Label_Statement"], RDF.type, mp["Statement"]))

        # Claim : is a research statement label qualified by assertion URI
        if item['researchStatementLabel']:
            graph.add((Literal(item["researchStatementLabel"]),RDF.type, mp["Claim"]))
            graph.add((Literal(item["researchStatementLabel"]), RDF.type, mp["Statement"]))

            if item['researchStatement']:
                graph.add((Literal(item["researchStatementLabel"]), mp["logicalClaim"], URIRef(item["researchStatement"])))
                graph.add((URIRef(item["researchStatement"]), RDF.type, mp["SemanticQualifier"]))

            else:
                graph.add((Literal(item["researchStatementLabel"]), mp["qualifiedBy"], Literal("stubbed out")))  


        # relationships
        graph.add((poc[currentAnnotItem], oa["hasBody"], poc[currentAnnotationStatement]))
        graph.add((poc[currentAnnotationStatement], mp["represents"], poc[currentAnnotItem]))
        
        if item['researchStatementLabel']:
            graph.add((poc[currentAnnotationStatement], mp["supports"], Literal(item["researchStatementLabel"])))
        else:
            graph.add((poc[currentAnnotationStatement], mp["supports"], Literal(item["stubbed out"])))


    ## add prefix, exact, postfix into dict
    item["prefix"] = prefix
    item["exact"] = exact
    item["postfix"] = postfix
    #print "ITEM:" + str(item)
    mp_list.append(item)


# display the graph
f = codecs.open(OUT_FILE,"w","utf8")
#graph.serialize(destination=f,format="xml",encoding="utf8")
s = graph.serialize(format="xml",encoding="utf8")

#f.write(graph.serialize(format="xml",encoding="utf8"))
f.write(unicode(s,errors='replace'))
#print graph.serialize(format="xml")
f.close
graph.close()


## write in tsv file
try:
    with open('../data/processed-dikb-observed-ddis.tsv', 'wb') as tsvfile:

        writer = csv.DictWriter(tsvfile, delimiter='\t', fieldnames=["prefix","postfix","exact","drug1","drug2","objectUri","ddiPkMechanism","contraindication","severity","source","dateAnnotated","precipUri","precaution","evidence","researchStatement",'uri',"object","precip","objectURI","precipURI","label","homepage","numericVal","contVal","ddiPkEffect","evidenceSource","evidenceType","evidenceStatement","dataAnnotated","whoAnnotated","researchStatementLabel"])
        writer.writeheader()
        writer.writerows(mp_list)
except:
    print "encoding exception.......  skipped"
    pass

