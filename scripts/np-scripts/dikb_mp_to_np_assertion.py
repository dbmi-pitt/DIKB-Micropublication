## dikb_mp_to_np_assertion.py
#
# Convert MP DIKB data to add nanopubs 
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
# $ python dikb_mp_to_np_assertion.py  ../../data/mp-graphs/initial-dikb-mp-oa.xml > ../../data/np-graphs/dikb-np-assertion.trig
# $ rapper -i trig -o rdfxml ../../data/np-graphs/dikb-np-assertion.trig > ../../data/np-graphs/dikb-np-assertion-for-inference.xml

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
	ds.namespace_manager.bind("ddi","http://dbmi-icode-01.dbmi.pitt.edu/mp/")
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

	pddiD = dict([line.split(',',1) for line in open('../../data/np-graphs/processed-dikb-ddis-for-nanopub.csv')])
	cL = dict([line.split('\t') for line in open('../../data/chebi_mapping.txt')])
	pL = dict([line.split('\t') for line in open('../../data/pro_mapping.txt')])
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
				
			if(predicateType == "increases_auc"):

				aURI =	URIRef("http://dbmi-icode-01.dbmi.pitt.edu/mp/ddi-spl-annotation-np-assertion-%s") % assertionCount
				assertionCount += 1
			
				bn1 = BNode('1')
				bn2 = BNode('2')
				bn3 = BNode('3')
				bn4 = BNode('4')
				bn5 = BNode('5')
				bn6 = BNode('6')
				bn7 = BNode('7')
				bn8 = BNode('8')
				bn9 = BNode('9')
				bn10 = BNode('10')

				assertionLabel = cL[claimSub.strip('\n')].strip('\n') + " - " + cL[claimObj.strip('\n')].strip('\n') + " potential drug-drug interaction"

				a = ds.add_graph((aURI))
				a.add(( aURI, RDF.type, np.assertion))
				a.add(( aURI, RDF.type, owl.Class))
				a.add(( aURI, RDFS.label, (Literal(assertionLabel.lower()))))	 
				a.add(( aURI, RDFS.subClassOf, URIRef("http://purl.obolibrary.org/obo/DIDEO_00000000")))
				a.add(( bn1, RDF.type, owl.Restriction))
				a.add(( bn1, owl.onProperty, URIRef("http://purl.obolibrary.org/obo/IAO_0000136")))
				a.add(( bn2, RDF.type, owl.Class))
				a.add(( bn3, RDF.first, URIRef("http://purl.obolibrary.org/obo/DIDEO_00000012")))
				a.add(( bn5, RDF.first, bn4))
				a.add(( bn3, RDF.rest, bn5))
				a.add(( bn4, RDF.type, owl.Restriction))
				a.add(( bn4, owl.onProperty, URIRef("http://purl.obolibrary.org/obo/BFO_0000052")))
				a.add(( bn4, owl.hasValue, URIRef(claimSub.strip('\n'))))
				a.add(( bn5, RDF.rest, RDF.nil))
				a.add(( bn2, owl.intersectionOf, bn3))
				a.add(( bn1, owl.someValuesFrom, bn2))
				a.add(( aURI, RDFS.subClassOf, bn1))
				a.add(( bn6, RDF.type, owl.Restriction))
				a.add(( bn6, owl.onProperty, URIRef("http://purl.obolibrary.org/obo/IAO_0000136")))
				a.add(( bn7, RDF.type, owl.Class))
				a.add(( bn8, RDF.first, URIRef("http://purl.obolibrary.org/obo/DIDEO_00000013")))
				a.add(( bn10, RDF.first, bn9))
				a.add(( bn8, RDF.rest, bn10))
				a.add(( bn9, RDF.type, owl.Restriction))
				a.add(( bn9, owl.onProperty, URIRef("http://purl.obolibrary.org/obo/BFO_0000052")))
				a.add(( bn9, owl.hasValue, URIRef(claimObj.strip('\n'))))
				a.add(( bn10, RDF.rest, RDF.nil))
				a.add(( bn7, owl.intersectionOf, bn8))
				a.add(( bn6, owl.someValuesFrom, bn7))
				a.add(( aURI, RDFS.subClassOf, bn6))

				ds.add(( aURI, mp.formalizes, b['c']))
				ds.add(( b['c'], mp.formalizedAs, aURI))
				
			elif(predicateType == "substrate_of"):
						
				aURI =	URIRef("http://dbmi-icode-01.dbmi.pitt.edu/mp/ddi-spl-annotation-np-assertion-%s") % assertionCount
				assertionCount += 1
				
				dLabel = cL[claimSub.strip('\n')].strip('\n')
				eLabel = pL[claimObj.strip('\n')].strip('\n')
				assertionLabel = dLabel + " substrate of " + eLabel

				a = ds.add_graph((aURI))
				ds.add(( aURI, RDF.type, np.assertion))
				ds.add(( aURI, RDFS.label, Literal(assertionLabel.lower())))				   
				ds.add(( aURI, mp.formalizes, b['c']))
				ds.add(( b['c'], mp.formalizedAs, aURI))
				
				a.add(( URIRef(claimObj.strip('\n')), RDF.type, URIRef("http://purl.obolibrary.org/obo/OBI_0000427")))
				a.add(( URIRef(claimObj.strip('\n')), RDFS.label, Literal(eLabel.lower())))
				a.add(( URIRef(claimObj.strip('\n')), URIRef("http://purl.obolibrary.org/obo/DIDEO_00000096"), URIRef(claimSub.strip('\n'))))

				a.add(( URIRef(claimSub.strip('\n')), RDF.type, URIRef("http://purl.obolibrary.org/obo/CHEBI_24431")))
				a.add(( URIRef(claimSub.strip('\n')), RDFS.label, Literal(dLabel.lower())))
				
			elif(predicateType == "inhibits"):

				aURI =	URIRef("http://dbmi-icode-01.dbmi.pitt.edu/mp/ddi-spl-annotation-np-assertion-%s") % assertionCount
				assertionCount += 1
				
				dLabel = cL[claimSub.strip('\n')].strip('\n')
				eLabel = pL[claimObj.strip('\n')].strip('\n')
				assertionLabel = dLabel + " inhibits " + eLabel
				
				a = ds.add_graph((aURI))
				ds.add(( aURI, RDF.type, np.assertion))
				ds.add(( aURI, RDFS.label, Literal(assertionLabel.lower())))
				ds.add(( aURI, mp.formalizes, b['c']))
				ds.add(( b['c'], mp.formalizedAs, aURI))
				
				a.add(( URIRef(claimSub.strip('\n')), RDF.type, URIRef("http://purl.obolibrary.org/obo/CHEBI_24431")))
				a.add(( URIRef(claimSub.strip('\n')), RDFS.label, Literal(dLabel.lower())))
				a.add(( URIRef(claimSub.strip('\n')), URIRef("http://purl.obolibrary.org/obo/RO_0002449"), URIRef(claimObj.strip('\n'))))

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
