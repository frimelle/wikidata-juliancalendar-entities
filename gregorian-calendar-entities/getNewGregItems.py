# This Python file uses the following encoding: utf-8
#!/usr/bin/python
from SPARQLWrapper import SPARQLWrapper, JSON
import csv
from collections import defaultdict
import urllib2
import json

dates_query = """
SELECT ?entity ?property ?timeString
WHERE {
  ?entity ?property ?valueNode.
  ?valueNode <http://www.wikidata.org/ontology#preferredCalendar>
<http://www.wikidata.org/entity/Q1985727>.
  ?valueNode <http://www.wikidata.org/ontology#time> ?timeString.
  FILTER (?timeString < "1500-01-01"^^xsd:date).
} GROUP BY ?entity
"""
sparqlDict = {}

def url_opener(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Script to get the statistics, lucie.kaffee@wikimedia.de')]
    infile = opener.open(url)
    page = json.load(infile)
    return page


def queryData( sparql_query ):
    try:
        sparql = SPARQLWrapper( "http://milenio.dcc.uchile.cl/sparql" )
        sparql.setQuery( sparql_query )
        sparql.setReturnFormat( JSON )
        results = sparql.query().convert()
        return results
    except Exception, e:
        raise e


def getSPARQLdata():
    sparqlList = []
    results = queryData( dates_query )
    #write results in List
    for result in results["results"]["bindings"]:
        timeString = result["timeString"]['value']
        if not '<http://www.w3.org/2001/XMLSchema#gYear>' in timeString:
            if not '-01-01-03:00' in timeString:
                entity_id = result["entity"]['value'].split('S')[0].split('entity/')[1]
                prop = result["property"]['value'].split('q')[0].split('entity/')[1]
                if 'r' in prop:
                    prop = prop.split('r')[0]
                if 'v' in prop:
                    prop = prop.split('v')[0]

                history(entity_id, prop)

    print "SPARQL list: " + str(len( sparqlList ))


def history(entity_id, prop):
    page = url_opener("https://www.wikidata.org/w/api.php?action=query&prop=revisions&titles=" + entity_id + "&rvlimit=500&rvprop=timestamp|user|comment|ids&indexpageids=1&format=json")
    pageids = page['query']['pageids']
    for pageid in pageids:
        if 'revisions' in page['query']['pages'][pageid]:
            for revision in page['query']['pages'][pageid]['revisions']:
                if prop in revision['comment']:
                    if not 'wbsetreference' in revision['comment']:
                        if not entity_id in sparqlDict:
                            sparqlDict[entity_id] = 'http://www.wikidata.org/w/index.php?title=' + entity_id + '&diff=' + str(revision['revid'])
                        else:
                            sparqlDict[entity_id] = 'http://www.wikidata.org/w/index.php?title=' + entity_id + '&diff=' + str(revision['revid']) + " " + str(sparqlDict[entity_id])


def writeFile(file, list):
     f = open( file, 'w+' )
     for item in list:
         f.write(item + " " + 'http://wikidata.org/entity/' + list.get(item) + '\n')
     f.close()

getSPARQLdata()
writeFile('gregItems.txt', sparqlDict)

#writeFile('newItems.txt', getSPARQLdata())
