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
import pickle
import difflib


## import Sparql-related
from SPARQLWrapper import SPARQLWrapper, JSON

## import RDF related
from rdflib import Graph, BNode, Literal, Namespace, URIRef, RDF, RDFS

## to retrieve from PubMed
from Bio.EUtils  import HistoryClient

################################################################################
# Globals
################################################################################
PRE_POST_CHARS=50
OUT_FILE="../data/initial-dikb-mp-oa-Aug2014.xml"
# THE GLOBAL QUERY CLIENT
client1 = HistoryClient.HistoryClient()

################################################################################
# Functions
################################################################################

## TODO: modify this function to correctly retrieve PubMed abstracts using PMIDs
def retrieveByEUtils(pmid, limit=None):
    rslt_D = {}
    q = '''%s [UID]''' % (pmid)
    rslts = client1.search(q)

    print "INFO: %d results" % len(rslts)
    
    if len(rslts) == 1:
        rec = rslts[0].efetch(retmode = "text", rettype = "abstract").read()
        id = re.findall("PMID: \d+",rec)
        id = " ".join(id)
        id = id[6:]
        newD = {"pmid":id,
                "abstract":rec}
                
        rslt_D[id] = newD

    return rslt_D

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
lsplsparql = SPARQLWrapper("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/sparql")

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
data_set = pickle.load( open( "../data/dikb-observed-ddis.pickle", "rb" ) )

annotationSetCntr = 1
annotationItemCntr = 1
annotationBodyCntr = 1
annotationEvidenceCntr = 1
annotationReStatementCntr = 1
splSetIdCache = {} 

graph = Graph()

## TODO: the code needs to be modified so that the same targets have multiple bodies if that is necessary

for item in data_set:     ## <-------- Use the list of PDDI dictionary instances from the pickle

    ###################################################################
    ### EACH SPL HAS A SET OF ANNOTATIONS, EACH WITH A TARGET AND BODY 
    ###################################################################
    setid = item["evidenceSource"].replace("http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/resource/structuredProductLabelMetadata/","") 
    print setid

    if setid not in splSetIdCache.keys():
        currentAnnotSet = 'ddi-spl-annotation-set-%s' % annotationSetCntr # this is what is indicated by "ex:" in the diagram, a resource with a unique id. I recall that the convention is used in the Open Data Annotation specification too
        splSetIdCache[setid] = currentAnnotSet
        annotationSetCntr += 1
        
        graph.add((poc[currentAnnotSet], RDF.type, oa["DataAnnotation"])) # TODO: find out what is being used for collections in OA
        graph.add((poc[currentAnnotSet], oa["annotatedAt"], Literal(datetime.date.today())))
        graph.add((poc[currentAnnotSet], oa["annotatedBy"], URIRef(u"http://www.pitt.edu/~rdb20/triads-lab.xml#TRIADS")))
        graph.add((poc[currentAnnotSet], oa["hasSource"], Literal(item["evidenceSource"]))) 
         
    else:
        currentAnnotSet = splSetIdCache[setid]
         
    currentAnnotItem = "ddi-spl-annotation-item-%s" % annotationItemCntr
    annotationItemCntr += 1

    graph.add((poc[currentAnnotSet], aoOld["item"], poc[currentAnnotItem])) # TODO: find out what is being used for items of collections in OA
    graph.add((poc[currentAnnotItem], RDF.type, oa["DataAnnotation"]))
    graph.add((poc[currentAnnotItem], oa["annotatedAt"], Literal(item["dateAnnotated"])))
    graph.add((poc[currentAnnotItem], oa["annotatedBy"], Literal(item["whoAnnotated"]))) # TODO: add 'boycer' to the TRIADS graph and change this annotatedBy to use #boycer
    graph.add((poc[currentAnnotItem], oa["motivatedBy"], oa["tagging"]))
    
### SPECIFY THE TARGET OF THE ANNOTATION - FOR THIS PROJECT, TARGETS ARE ONE OR MORE PORTIONS OF TEXT FROM A GIVEN SPL
    currentAnnotItemUuid = URIRef(u"urn:uuid:%s" % uuid.uuid4())
    textConstraintUuid = URIRef(u"urn:uuid:%s" % uuid.uuid1())

    graph.add((poc[currentAnnotItem], oa["hasTarget"], currentAnnotItemUuid))

    if item["evidenceType"] == u'http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#Non_traceable_Drug_Label_Statement':
        graph.add((currentAnnotItemUuid, oa["constrains"], Literal(u"http://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=%s" % unicode(setid))))
    else:
        ## TODO: handle those items from the scientific literature  - i.e., sources from PubMed
        continue

    graph.add((currentAnnotItemUuid, RDF.type, poc["SPLConstrainedTarget"]))
    graph.add((currentAnnotItemUuid, RDF.type, oa["ConstrainedTarget"]))
    graph.add((currentAnnotItemUuid, oa["constrainedBy"], textConstraintUuid))
         
    graph.add((textConstraintUuid, RDF.type, oa["SpecificResource"]))
    graph.add((textConstraintUuid, RDF.type, poc["SPLConstrainedTarget"]))

    contentD == {}
    if item["evidenceType"] != u'http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#Non_traceable_Drug_Label_Statement':
        ## TODO: handle those items from the scientific literature  - i.e., sources from PubMed. Use eutils to retrieve the abstract
    else:
        ## TODO: handle those items from the structured product labels

        ## TODO: locate the section within the SPL
        # The process would be something like this:
        # 1. extract the 'exact' drug interaction statement (i.e., the string that is the exact quote from the product label)
        # 2. identify the 'pre' and 'post' string. 
        # 2a. First, acquire the text for the sections that are important in the SPL that is indicated by the setid
        # 2b. then search for the 'exact' string in each section until you find a match.
        # 2c. then pull the 'pre' and 'post' text - say 50 characters (PRE_POST_CHAR_NUM = 50)
        # NOTE: its important to process the text as Unicode (e.g., a bytestream)
        print "GETTING SECTIONS FOR SETID: %s" % setid
        
        try:
            contentD = getSPLSectionsSparql(setid, lsplsparql)
        except urllib2.HTTPError:
            print "There is a problem retreiving the SPL content for setid %s. %s" % (setid, urllib2.HTTPError)

    if contentD == {}:
        continue
        
    ####extract the 'exact' drug interaction statement
    index_quoted = item["evidenceStatement"].find('Quote') ## TODO: use a regular expression because the quote syntax is sometimes slightly different
    
    if index_quoted > 0:
        exact=item["evidenceStatement"][index_quoted:]
    else:
        exact=item["evidenceStatement"]
        
    rgx = re.compile(u"quote ?:", re.I)
    exact = rgx.sub(u"",exact)

    
    ####identify the 'pre' and 'post' string
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
        
    print max_match
    print index_exact

    if index_exact < PRE_POST_CHARS:
        prefix = section_text[0:index_exact]
    else: 
        prefix = section_text[0:PRE_POST_CHARS]

    if index_exact + len(exact) + PRE_POST_CHARS > len(section_text):
        postfix = section_text[index_exact+len(exact):]
    else:
        postfix = section_text[index_exact+len(exact):index_exact+len(exact)+PRE_POST_CHARS]

		      	  
    print u"EXACT: %s" % exact
	
    print u"PRE: %s" % prefix
	
    print u"POST: %s" % postfix
        
    graph.add((textConstraintUuid, oa["exact"], Literal(exact)))
    graph.add((textConstraintUuid, oa["prefix"], Literal(prefix)))
    graph.add((textConstraintUuid, oa["postfix"], Literal(postfix))) 


    ## SPECIFY THE BODIES OF THE ANNOTATION - FOR THIS PROJECT, EACH
    ##  BODY CONTAINS A DDI SEMANTIC LABEL ASSIGNED TO THE TARGET
    currentAnnotationBody = "ddi-spl-annotation-body-%s" % annotationBodyCntr
    annotationBodyCntr += 1
         
    graph.add((poc[currentAnnotItem], oa["hasBody"], poc[currentAnnotationBody]))
    graph.add((poc[currentAnnotationBody], RDF.type, poc["PDDIStatement"])) # TODO: this is not yet formalized in a public ontology but should be
    graph.add((poc[currentAnnotationBody], RDFS.label, Literal("%s (object) - %s (precipitant)" % (item["object"], item["precip"]))))

    #SIO Describes
    graph.add((poc[currentAnnotationBody], sio["SIO_000563"], poc["PharmacokineticImpact"]))  
    graph.add((poc[currentAnnotationBody], poc["PharmacokineticImpact"], poc['metabolism-decrease']))

    #SIO refers to
    graph.add((poc[currentAnnotationBody], sio["SIO_000628"], dikbD2R['ObjectDrugOfInteraction']))
    graph.add((poc[currentAnnotationBody], dikbD2R['ObjectDrugOfInteraction'], URIRef(item["objectURI"])))
    
    graph.add((poc[currentAnnotationBody], sio["SIO_000628"], dikbD2R['PrecipitantDrugOfInteraction']))
    graph.add((poc[currentAnnotationBody], dikbD2R['PrecipitantDrugOfInteraction'], URIRef(item["precipURI"])))
    
    #ex: evidence
    graph.add((URIRef(item["evidence"]), siocns["content"], poc[currentAnnotItem]))
    graph.add((URIRef(item["evidence"]), RDF.type, ncbit["Evidence"])) 
    graph.add((URIRef(item["evidence"]), dikbEvidence["EvidenceType"], dikbEvidence["Non_traceable_Drug_Label_Statement"])) 
    
    #ex:researchStatement
    graph.add((URIRef(item["researchStatement"]), swande["citesAsSupportiveEvidence"],URIRef(item["evidence"]))) 
    graph.add((URIRef(item["researchStatement"]), RDF.type, swande["ResearchStatement"]))  
    graph.add((URIRef(item["researchStatement"]), RDFS.label, Literal(item['researchStatementLabel']))) 

# display the graph
f = codecs.open(OUT_FILE,"w","utf8")
#graph.serialize(destination=f,format="xml",encoding="utf8")
s = graph.serialize(format="xml",encoding="utf8")

#f.write(graph.serialize(format="xml",encoding="utf8"))
f.write(unicode(s,errors='replace'))
#print graph.serialize(format="xml")
f.close

graph.close()





