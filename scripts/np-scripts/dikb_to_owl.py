## dikb_to_owl.py
#
# Convert MP DIKB data to owl format for use in property chains
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
# $ python dikb_to_owl.py  ../data/mp-graphs/initial-dikb-mp-oa.xml > ../data/np-graphs/initial-nanopub-owl.trig
# $ rapper -i trig -o turtle ../data/np-graphs/initial-nanopub-owl.trig > ../data/np-graphs/initial-nanopub-owl.turtle

import sys

import argparse

import uuid

## import Sparql-related
from SPARQLWrapper import SPARQLWrapper, JSON

## import RDF related
from rdflib import Graph, BNode, Literal, Namespace, URIRef, RDF, RDFS, XSD, Dataset

from pprint import pprint

###################
# QUERIES

interactSelect = '''
PREFIX mp: <http://purl.org/mp/>

SELECT ?c
WHERE
{
  ?c a mp:Claim.
}
ORDER BY ?c
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

	assertionCount = 1
	enzymeCount = 1

	pddiD = dict([line.split(',',1) for line in open('../data/processed-dikb-ddis-for-nanopub.csv')])
	cL = dict([line.split('\t') for line in open('../data/chebi_mapping.txt')])
	pL = dict([line.split('\t') for line in open('../data/pro_mapping.txt')])
	substrateD = {}
	inhibitorD = {}
			
	bindings = g.query(interactSelect)
	for b in bindings:

		if( pddiD.has_key(str(b['c'].decode('utf-8'))) ):
			tempClaim = pddiD[ str(b['c'].decode('utf-8')) ]
			claimInfo = tempClaim.split(',')
			claimSub = claimInfo[1]
			claimObj = claimInfo[2]
			predicateType = claimInfo[0].strip('\n')
				
			if(predicateType == "substrate_of"):
						
				dLabel = cL[claimSub.strip('\n')].strip('\n')
				eLabel = pL[claimObj.strip('\n')].strip('\n')

				ds.add(( URIRef(claimObj.strip('\n')), RDF.type, owl.NamedIndividual))
				ds.add(( URIRef(claimObj.strip('\n')), RDF.type, URIRef("http://purl.obolibrary.org/obo/OBI_0000427")))
				ds.add(( URIRef(claimObj.strip('\n')), RDFS.label, Literal(eLabel.lower())))
				ds.add(( URIRef(claimObj.strip('\n')), URIRef("http://purl.obolibrary.org/obo/DIDEO_00000096"), URIRef(claimSub.strip('\n'))))

				ds.add(( URIRef(claimSub.strip('\n')), RDF.type, owl.NamedIndividual))
				ds.add(( URIRef(claimSub.strip('\n')), RDF.type, URIRef("http://purl.obolibrary.org/obo/CHEBI_24431")))
				ds.add(( URIRef(claimSub.strip('\n')), RDFS.label, Literal(dLabel.lower())))
				
			elif(predicateType == "inhibits"):

				dLabel = cL[claimSub.strip('\n')].strip('\n')
				eLabel = pL[claimObj.strip('\n')].strip('\n')


				ds.add(( URIRef(claimSub.strip('\n')), RDF.type, owl.NamedIndividual))
				ds.add(( URIRef(claimSub.strip('\n')), RDF.type, URIRef("http://purl.obolibrary.org/obo/CHEBI_24431")))
				ds.add(( URIRef(claimSub.strip('\n')), RDFS.label, Literal(dLabel.lower())))
				ds.add(( URIRef(claimSub.strip('\n')), URIRef("http://purl.obolibrary.org/obo/RO_0002449"), URIRef(claimObj.strip('\n'))))

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
