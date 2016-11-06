from mprorp.utils import home_dir
import os
from mprorp.db.dbDriver import *
from mprorp.db.models import *

#text = get_doc('f844e3f0-4b02-4643-9ee3-2bdcd7c422be')
#print(text)
#x = open('C:/Users/User/Desktop/try.txt', 'w', encoding='utf-8')
#x.write('1')
#x.close()
#print(os.path.dirname(os.path.realpath(__file__)))
#path = os.path.dirname(os.path.realpath(__file__))
#os.chdir(path + '/grammars')
session = db_session()
type1 = session.query(KLADR.name).filter_by(level=1, type="Город").all()
print(type1)