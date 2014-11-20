import sys

import argparse

## import Sparql-related
from SPARQLWrapper import SPARQLWrapper, JSON

## import RDF related
from rdflib import Graph, BNode, Literal, Namespace, URIRef, RDF, RDFS, XSD, Dataset


from pprint import pprint

###################
# QUERIES

interactSelect = '''
PREFIX dikbD2R: <http://dbmi-icode-01.dbmi.pitt.edu/dikb/vocab/resource/> 

SELECT ?inter ?o ?s
WHERE {
    ?inter dikbD2R:ObjectDrugOfInteraction ?o.
    ?inter dikbD2R:PrecipitantDrugOfInteraction ?s.
}
'''
##################

sio = Namespace('http://semanticscience.org/resource/')
np = Namespace('http://www.nanopub.org/nschema#')

def createNanopubs(g):
	ds = Dataset()
	ds.namespace_manager.bind("ddi","http://purl.org/net/nlprepository/spl-ddi-annotation-poc#")
	
	bindings = g.query(interactSelect)
	for b in bindings:
		npURI = URIRef(b['inter'] + "-nanopub")
		headURI = URIRef(b['inter'] + "-head")
		aURI =  URIRef(b['inter'] + "-assertion")
		pubInfoURI = URIRef(b['inter'] + "-pubInfo")
		provURI = URIRef(b['inter'] + "-provenance")
		
		
		head = ds.add_graph(headURI)
		head.add((npURI, RDF.type, np['Nanopublication']))
		head.add((aURI, RDF.type, np['Assertion']))
		head.add((provURI, RDF.type, np['Provenance']))
		head.add((pubInfoURI, RDF.type, np['PublicationInfo']))
		head.add((npURI, np['hasAssertion'], aURI))
		head.add((npURI, np['hasProvenance'], provURI))
		head.add((npURI, np['hasPublicationInfo'], pubInfoURI))

		#print head.serialize()
		
		a = ds.add_graph(aURI)
		a.add((b['s'], URIRef('http://dbmi-icode-01.dbmi.pitt.edu/dikb/vocab/interactsWith'), b['o']))
		a.add((b['s'], RDF.type, sio["SIO_010038"]))
		a.add((b['o'], RDF.type,  sio["SIO_010038"]))
		
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