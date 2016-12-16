import mprorp.ner.wiki_search as wiki_search
import mprorp.db.dbDriver as Driver
from mprorp.db.models import Gazetteer

names = wiki_search.all_names_rus()

session = Driver.db_session()
new_gaz = Gazetteer(gaz_id='names_from_wikidata_16_12_16', name='names', lemmas=list(names))
session.add(new_gaz)
session.commit()
