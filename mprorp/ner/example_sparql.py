import requests

query = '''PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?president ?cause ?dob ?dod WHERE {
    ?pid wdt:P39 wd:Q11696 .
    ?pid wdt:P509 ?cid .
    ?pid wdt:P569 ?dob .
    ?pid wdt:P570 ?dod .

    OPTIONAL {
        ?pid rdfs:label ?president filter (lang(?president) = "en") .
    }
    OPTIONAL {
        ?cid rdfs:label ?cause filter (lang(?cause) = "en") .
    }
}'''


label = 'Алексей Навальный'
language = 'ru'
query = '''PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?id ?name ?family_name WHERE {
    ?id ?label "''' + label + '"@' + language + ''' .
    ?id wdt:P31 wd:Q5 .
    OPTIONAL {
        ?id wdt:P734 ?family_name_entity .
        ?family_name_entity rdfs:label ?family_name filter (lang(?family_name) = "ru").
        }
    OPTIONAL {
        ?id wdt:P735 ?name_entity .
        ?name_entity rdfs:label ?name filter (lang(?name) = "ru") .
        }
    }'''

url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
data = requests.get(url, params={'query': query, 'format': 'json'}).json()

presidents = []
for item in data['results']['bindings']:
    print(item['id']['value'])
    if 'name' in item:
        print(item['name']['value'])
    if 'family_name' in item:
        print(item['family_name']['value'])

#     presidents.append({
#         'id': item['id']['value'],
#         'name': item['name']['value']})
#
# print(presidents)


