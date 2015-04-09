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
  ?entity ?property ?valueNode .
  ?valueNode <http://www.wikidata.org/ontology#preferredCalendar>
<http://www.wikidata.org/entity/Q1985786> .
  ?valueNode <http://www.wikidata.org/ontology#time> ?timeString .
}
"""

date = '2014-05-01'

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
        if not '<http://www.w3.org/2001/XMLSchema#gYear>' in result["timeString"]['value']:
        
            entity_id = result["entity"]['value'].split('S')[0].split('entity/')[1]
            prop = result["property"]['value'].split('q')[0].split('entity/')[1]
            if 'r' in prop:
                prop = prop.split('r')[0]
            if 'v' in prop:
                prop = prop.split('v')[0]

            if checkTime(entity_id, prop): 

                sparqlList.append( entity_id )

    print "SPARQL list: " + str(len( sparqlList ))
    return sparqlList

### check if items are edited before a certain date
def checkTime(entity_id, prop):
    page = url_opener("https://www.wikidata.org/w/api.php?action=query&prop=revisions&titles=" + entity_id + "&rvlimit=500&rvprop=timestamp|user|comment|ids&indexpageids=1&format=json")
    pageids = page['query']['pageids']
    for pageid in pageids: 
        if 'revisions' in page['query']['pages'][pageid]:
            for revision in page['query']['pages'][pageid]['revisions']:
                if prop in revision['comment']:
                    if not 'wbsetreference' in revision['comment']:
                        if revision['timestamp'] < date:
                            if not entity_id in sparqlDict:
                                sparqlDict[entity_id] = 'http://www.wikidata.org/w/index.php?title=' + entity_id + '&diff=' + str(revision['revid'])
                            else: 
                                sparqlDict[entity_id] = 'http://www.wikidata.org/w/index.php?title=' + entity_id + '&diff=' + str(revision['revid']) + " " + str(sparqlDict[entity_id])
                            return True
            


def getCSVdata( csvfile ):
    columns = defaultdict( list ) # each value in each column is appended to a list
    data = []

    with open( csvfile, 'rb' ) as csvfile:
        reader = csv.DictReader( csvfile ) # read rows into a dictionary format
        for row in reader:
            for ( k,v ) in row.items(): # go over each column name and value
                columns[k].append( v ) # append the value into the appropriate list
                                     # based on column name k

    data = columns['entity_id']
    print "CSV list: " + str(len( data ))
    return data

def writeFile(file, list):
     f = open( file, 'w+' )
     for item in list:
         f.write('http://wikidata.org/wiki/' + item + '\n')
     f.close()

### this part is to compare with a csv file
def compareLists():
    sparqlList = getSPARQLdata()
    csvList = getCSVdata( 'JulianCalendarChanges.csv' )
    newItems = list( set( sparqlList ) - set( csvList ) )
    print "New list: " + str(len( newItems ))
    return newItems

def createItemPropList():
    comparedLists = compareLists()
    resultList = []
    for c in comparedLists:
        resultList.append(c + " " + sparqlDict.get(c))
    return resultList

writeFile('newItems-prop-new.txt', createItemPropList())

#writeFile('newItems.txt', getSPARQLdata())
