import requests

def find_human(label, language = 'ru'):
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
        my_item = dict()
        my_item['id'] = item['id']['value']
        if 'name' in item:
            my_item['name'] = item['name']['value']
        if 'family_name' in item:
            my_item['family_name'] = item['family_name']['value']
        humans.append(my_item)

    return humans


def is_given_name(label,  language = 'ru'):
    query = '''PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT * WHERE
    {
        {
        ?s rdfs:label "''' + label + '"@' + language + '''.
        ?s  wdt:P31 wd:Q12308941
        } UNION {
        ?s rdfs:label "''' + label + '"@' + language + '''.
        ?s  wdt:P31 wd:Q11879590
        } UNION {
        ?s rdfs:label "''' + label + '"@' + language + '''.
        ?s  wdt:P31 wd:Q202444
        }UNION {
        ?s rdfs:label "''' + label + '"@' + language + '''.
        ?s  wdt:P31 wd:Q3409032
        }
    } '''
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    data = requests.get(url, params={'query': query, 'format': 'json'}).json()

    answer = False
    for item in data['results']['bindings']:
        answer = True
        break

    return answer