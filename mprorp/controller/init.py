"""some code for mpro init"""
import re
import sys
pat = re.compile("/([a-zA-Z]+).pid")
string = "".join(sys.argv)
worker = pat.search(string)
if worker:
    worker = worker.groups()[0]
else:
    worker = False
flask_instance = string.find('gunicorn') != -1
central_instance = string.find('central') != -1

if worker in ["default", "theme"]:
    from mprorp.analyzer.pymystem3_w import Mystem
    global_mystem = Mystem()
