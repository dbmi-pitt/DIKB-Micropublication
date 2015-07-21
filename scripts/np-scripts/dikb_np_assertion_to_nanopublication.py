## dikb_np_assertion_to_nanopublication.py
#
# Convert NP:Assertion into full nanopublication
#
## The Drug Interaction Knowledge Base (DIKB) is (C) Copyright 2005 - 2015 by
## Richard Boyce

## Original Authors:
##	 Paul Groth, Richard Boyce, Samuel Rosko, Yifan Ning, Jodi Schneider, Tim Clark, Paolo Ciccarese

## This code is licensed under Apache License Version 2.0, January
## 2004. Please see the license in the root folder of this project

#
# NOTE: Requires Python RDFLib >=4.2
#
# Example usage and conversion to data that can be loaded into Virtuoso 6.0
# $ python dikb_np_assertion_to_nanopublication.py ../../queries/np-queries/combined-results.xml > ../../data/np-graphs/dikb-full-nanopublications.trig

import sys

import argparse

import uuid

## import Time-related
from datetime import datetime, date, time

## import Sparql-related
from SPARQLWrapper import SPARQLWrapper, JSON

## import RDF related
from rdflib import Graph, BNode, Literal, Namespace, URIRef, RDF, RDFS, XSD, Dataset

from pprint import pprint

###################
# QUERIES

interactSelect = '''
PREFIX np: <http://www.nanopub.org/nschema#>
PREFIX mp: <http://purl.org/mp/>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?a ?t
WHERE
{
  ?a a np:assertion.
  ?a mp:qualifiedBy ?t.
}
'''
##################

sio = Namespace('http://semanticscience.org/resource/')
np = Namespace('http://www.nanopub.org/nschema#')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
owl = Namespace('http://www.w3.org/2002/07/owl#')
obo = Namespace('http://purl.obolibrary.org/obo/')
oboInOwl = Namespace('http://www.geneontology.org/formats/oboInOwl#')
xsd = Namespace('http://www.w3.org/2001/XMLSchema#')
dc = Namespace('http://purl.org/dc/elements/1.1/')
mp = Namespace('http://purl.org/mp/')
prov = Namespace('http://www.w3.org/ns/prov#')
dikbEvidence = Namespace('http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#')

def createNanopubs(g):
		
	ds = Dataset()
	ds.namespace_manager.bind("ddi","http://purl.org/net/nlprepository/spl-ddi-annotation-poc#")
	ds.namespace_manager.bind("np", "http://www.nanopub.org/nschema#")
	ds.namespace_manager.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
	ds.namespace_manager.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
	ds.namespace_manager.bind("owl", "http://www.w3.org/2002/07/owl#")
	ds.namespace_manager.bind("obo", "http://purl.obolibrary.org/obo/")
	ds.namespace_manager.bind("oboInOwl", "http://www.geneontology.org/formats/oboInOwl#")
	ds.namespace_manager.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
	ds.namespace_manager.bind("dc", "http://purl.org/dc/elements/1.1/")
	ds.namespace_manager.bind("mp", "http://purl.org/mp/")
	ds.namespace_manager.bind("prov", "http://www.w3.org/ns/prov#")
	ds.namespace_manager.bind("dikbEvidence", "http://dbmi-icode-01.dbmi.pitt.edu/dikb-evidence/DIKB_evidence_ontology_v1.3.owl#")
	
	bindings = g.query(interactSelect)
	for b in bindings:
		
		idIndex = b['a'].decode('utf-8').index('DIDEO_')
		asIndex = b['a'].decode('utf-8').index('-assertion')
		identifier = b['a'].decode('utf-8')[idIndex:asIndex]
		predicateType = b['t'].decode('utf-8')

		npURI = URIRef('http://purl.obolibrary.org/obo/%s-nanopub') % identifier
		headURI = URIRef('http://purl.obolibrary.org/obo/%s-head') % identifier
		pubInfoURI = URIRef('http://purl.obolibrary.org/obo/%s-pubInfo') % identifier
		provURI = URIRef('http://purl.obolibrary.org/obo/%s-provenance') % identifier
		aURI = URIRef('http://purl.obolibrary.org/obo/%s-assertion') % identifier

		ds.add(( aURI, RDF.type, np.assertion))
		
		head = ds.add_graph(headURI)
		head.add((npURI, RDF.type, np['Nanopublication']))
		head.add((provURI, RDF.type, np['Provenance']))
		head.add((pubInfoURI, RDF.type, np['PublicationInfo']))
		head.add((npURI, np['hasAssertion'], aURI))
		head.add((npURI, np['hasProvenance'], provURI))
		head.add((npURI, np['hasPublicationInfo'], pubInfoURI))

		pub = ds.add_graph(pubInfoURI)
		pub.add((npURI, prov.wasAttributedTo, URIRef('http://orcid.org/0000-0002-2993-2085')))
		pub.add((npURI, prov.generatedAtTime, Literal(datetime.now()) ))
		
		if(predicateType == "http://purl.obolibrary.org/obo/DIDEO_00000000"):

			provenance = ds.add_graph(provURI)
			provenance.add(( aURI, prov.wasAttributedTo, URIRef('http://orcid.org/0000-0002-2993-2085')))
			provenance.add(( aURI, prov.generatedAtTime, Literal(datetime.now()) ))
			provenance.add(( aURI, prov.wasDerivedFrom, Literal("Derived from the DIKB's evidence base using the listed belief criteria")))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_RCT ))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_NR ))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_Par_Grps ))						 
					
		elif(predicateType == "http://purl.obolibrary.org/obo/DIDEO_00000096"):

			provenance = ds.add_graph(provURI)
			provenance.add(( aURI, prov.wasAttributedTo, URIRef('http://orcid.org/0000-0002-2993-2085')))
			provenance.add(( aURI, prov.generatedAtTime, Literal(datetime.now()) ))
			provenance.add(( aURI, prov.wasDerivedFrom, Literal("Derived from the DIKB's evidence base using the listed belief criteria")))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_RCT ))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_NR ))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_Par_Grps )) 
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_CT_PK_Genotype ))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_CT_PK_Phenotype )) 
					
		elif(predicateType == "http://purl.obolibrary.org/obo/RO_0002449"):

			provenance = ds.add_graph(provURI)
			provenance.add(( aURI, prov.wasAttributedTo, URIRef('http://orcid.org/0000-0002-2993-2085')))
			provenance.add(( aURI, prov.generatedAtTime, Literal(datetime.now()) ))
			provenance.add(( aURI, prov.wasDerivedFrom, Literal("Derived from the DIKB's evidence base using the listed belief criteria")))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_RCT ))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_NR ))
			provenance.add(( aURI, prov.hadMember, dikbEvidence.EV_PK_DDI_Par_Grps )) 
						
	print ds.serialize(format='trig')

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('filename', metavar='name', type=str, help='file to process', nargs='+')
	args = parser.parse_args()
	#print args
	fnames = args.filename
	for fn in fnames:
		g = Graph()
		g.parse(fn)
		createNanopubs(g)

	
if __name__ == "__main__":
	main()
