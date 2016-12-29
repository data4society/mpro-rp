"""parsing yandex smi"""

from mprorp.db.dbDriver import *
from mprorp.db.models import *
import json
from mprorp.crawler.utils import send_get_request
from lxml.html import document_fromstring
import csv


def ya_smi_import():
    with open('ya_smi/ya_smi.json', 'r') as f:
        json_source = f.read()
    with open('ya_smi/out.csv', 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        json_obj = json.loads(json_source)
        filters = json_obj["filters"]
        regions = filters["region"]["items"]
        countryIds = filters["region"]["countryIds"]
        countries = filters["region"]["countries"]
        rubrics = filters["rubric"]["items"]
        types = filters["type"]["items"]
        smis = filters["agencies"]
        session = db_session()
        i = 0
        for smi_key in smis:
            smi = smis[smi_key]
            pub = Publisher()
            #print(smi)
            meta = dict()
            pub.name = smi["n"]
            row = []
            row.append(pub.name)
            meta["ya_alias"] = smi["i"]
            row.append(meta["ya_alias"])
            if smi["rg"] != "0":
                pub.region = regions[smi["rg"]]
                pub.country = countries[countryIds[smi["rg"]]]
                row.append(pub.region)
                row.append(pub.country)
            else:
                row.append("")
                row.append("")
            if smi["rb"] in rubrics:
                meta["rubric"] = rubrics[smi["rb"]]
                row.append(meta["rubric"])
            else:
                row.append("")
            if smi["t"] != "0":
                meta["ya_type"] = types[smi["t"]]
                row.append(meta["ya_type"])
            else:
                row.append("")

            url = "https://news.yandex.ru/smi/"+smi["i"]
            html_source = send_get_request(url, has_encoding=True, gen_useragent=True)
            doc = document_fromstring(html_source)
            smi_div = doc.xpath("//dl[@class='smi__info']")[0]
            elements = smi_div.xpath("//img[@class='image']")
            if len(elements):
                meta["logo"] = "https:"+elements[0].get("src")
                row.append(meta["logo"])
            else:
                row.append("")
            elements = smi_div.xpath("//div[@class='smi__name']")
            if len(elements):
                meta["last"] = elements[0].text_content()
                row.append(meta["last"])
            else:
                row.append("")
            elements = smi_div.xpath("//dd[@class='smi__description']")
            if len(elements):
                pub.desc = elements[0].text_content()
                row.append(pub.desc)
            else:
                row.append("")
            elements = smi_div.xpath("//dd[@class='smi__chief-value']")
            if len(elements):
                meta["chief"] = elements[0].text_content()
                row.append(meta["address"])
            else:
                row.append("")
            elements = smi_div.xpath("//dd[@class='smi__address-value']")
            if len(elements):
                meta["address"] = elements[0].text_content()
                row.append(meta["address"])
            else:
                row.append("")
            elements = smi_div.xpath("//dd[@class='smi__phone-value']")
            if len(elements):
                meta["phone"] = elements[0].text_content()
                row.append(meta["phone"])
            else:
                row.append("")
            elements = smi_div.xpath("//dd[@class='smi__website-value']")
            if len(elements):
                pub.site = elements[0].find("a").get("href")
                row.append(pub.site)
            else:
                row.append("")
            elements = smi_div.xpath("//a[@itemprop='email']")
            if len(elements):
                meta["mail"] = elements[0].get("href").split(":")[1]
                row.append(meta["mail"])
            else:
                row.append("")
            pub.meta = meta
            pub.type = "ya_news"
            row.append(pub.type)
            session.add(pub)
            i+=1
            if i%10 == 0:
                session.commit()
                print(i)
            spamwriter.writerow(row)

        session.commit()
        print(i)
        session.remove()