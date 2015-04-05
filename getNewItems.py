# This Python file uses the following encoding: utf-8
#!/usr/bin/python
from SPARQLWrapper import SPARQLWrapper, JSON
import csv
from collections import defaultdict

dates_query = """
SELECT ?entity ?timeString
WHERE {
  ?entity ?property ?valueNode .
  ?valueNode <http://www.wikidata.org/ontology#preferredCalendar>
<http://www.wikidata.org/entity/Q1985786> .
  ?valueNode <http://www.wikidata.org/ontology#time> ?timeString .
}
"""
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
        if '<http://www.w3.org/2001/XMLSchema#gYear>' in result["timeString"]['value']:
            continue
        entity_id = result["entity"]['value'].split('S')[0].split('entity/')[1]
        sparqlList.append( entity_id )
    print len( sparqlList )
    return sparqlList

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
    print len( data )
    return data

def writeFile(file, list):
     f = open( file, 'w+' )
     for item in list:
         f.write('http://wikidata.org/wiki/' + item + '\n')
     f.close()

### this part is to compare with a csv file, commented out to make it testable
'''
def compareLists():
    sparqlList = getSPARQLdata()
    csvList = getCSVdata( 'JulianCalendarChanges.csv' )
    newItems = list( set( sparqlList ) - set( csvList ) )
    len( newItems )
    return newItems

writeFile('newItems.txt', compareLists())
'''
writeFile('newItems.txt', getSPARQLdata())
