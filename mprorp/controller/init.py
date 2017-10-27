"""some code for mpro init"""
import re
import sys
pat = re.compile("/([a-zA-Z]+).pid")
string = "".join(sys.argv)
worker = pat.search(string).groups()[0]

if worker in ["default", "theme"]:
    from mprorp.analyzer.pymystem3_w import Mystem
    global_mystem = Mystem()
