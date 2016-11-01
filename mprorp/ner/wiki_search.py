import requests

def find_human(label, language = 'ru'):
    query = '''PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?id ?dob WHERE {
    ?id ?label "''' + label + '"@' + language + ''' .
    ?id wdt:P31 wd:Q5 .
    ?id wdt:P569 ?dob
    }'''

    # '''OPTIONAL {
    #         ?pid rdfs:label ?president filter (lang(?president) = "en") .
    #     }
    #     OPTIONAL {
    #         ?cid rdfs:label ?cause filter (lang(?cause) = "en") .
    #     }
    # }'''

    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    data = requests.get(url, params={'query': query, 'format': 'json'}).json()

    humans = []
    for item in data['results']['bindings']:
        humans.append({
            'id': item['id']['value'],
            'dob': item['dob']['value']})

    return humans
