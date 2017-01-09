"""script for testing readability algorithms"""
import mprorp.crawler.readability.readability_com as read_com
import mprorp.crawler.readability.lxml_readability as read_lxml
import mprorp.crawler.readability.readability2 as read2
#import mprorp.crawler.readability.breadability as bread
import mprorp.crawler.readability.readability_kingwkb as kingwkb
import csv
from mprorp.crawler.readability.shingling import get_compare_estimate
from mprorp.crawler.utils import *
import urllib.request
from urllib.error import *
from readability.encoding import get_encoding
import html
import datetime

# links whick blocked by cloudflare firewall
cloudflare_links = ['http://podrobnosti.ua/2115445-frantsuzy-edut-rassledovat-zaderzhanie-sbu-terrorista.html', 'http://ryb.ru/2016/06/21/348972',
    'http://ryb.ru/2016/06/21/348890', 'http://ryb.ru/2016/06/21/349088',
    'http://www.aysor.am/ru/news/2016/06/21/%D1%81%D0%B5%D1%84%D0%B8%D0%BB%D1%8F%D0%BD/1100847',
    'http://news.am/rus/news/333253.html',
    'http://news.am/rus/news/333232.html',
    'http://news.am/rus/news/333247.html',
    'http://u-f.ru/News/politics/u9/2016/06/18/101730',
    'http://newsday24.org/11294-savchenko-ustala-ot-takoy-zhizni.html']

bad_links = ['http://kaliningradfirst.ru/207107', 'http://vzglyadpenza.ru/2016/06/gricak-govorit-chto-siriyci-priezzhali-v-ukrainskoe/', 'http://avtoinsider.com/rukovoditel-sbu-v-dnepre-i-oblasti-net-lagerya-dzhihadistov/', 'http://ryb.ru/2016/06/21/348972', 'http://ryb.ru/2016/06/21/348890', 'http://ryb.ru/2016/06/21/349088', 'http://lastnews.com.ua/novosti-ukraini/515506-ne-zhelayu-nikomu-imet-takogo-soseda-kak-rossiya.html', 'http://svodka.net/index.php?option=com_content&view=article&id=40969:v-lnr-boeviki-zaderjali-ukrainskuyu-jurnalistku&catid=236:obshestvoekonomika', 'http://newsera.ru/2016/06/187085/terroristi-lnr-soobschili-chto-yakobi-zaderzhali.html', 'http://lratvakan.com/news/212802.html', 'http://07kbr.ru/2016/06/18/mariya-zaxarova-v-efire-rt-prizvala-dzhona-kerri-byt-terpelivym/', 'http://topre.ru/2016/06/18/zaharova-k-bolelschikam-vo-francii-v-ryade-sluchaev.html', 'http://echospb.ru/2016/06/22/v-sb-ukraini-soobschili-chto-v-gosudarstve-net-baz-po/', 'http://belrynok.ru/2016/06/v-lnr-soobschili-o-zaderzhanii-zhurnalistiki-iz-ivano/', 'http://lastnews.com.ua/novosti-ukraini/515565-v-lnr-zaderzhali-zhurnalistku-iz-ivano-frankovska.html', 'http://morning-news.ru/2016/06/v-lnr-soobschili-o-zaderzhanii-ukrainskoy-zhurnalistki/', 'http://newsday24.org/11294-savchenko-ustala-ot-takoy-zhizni.html', 'http://www.moscow-post.com/news/society/vitse-premjer_karelii_popal_pod_podozrenie94812/', 'http://lastnews.com.ua/novosti-ukraini/515616-plenenie-ukrainskoy-zhurnalistki-v-luganske-poyavilas-reakciya-redakcii.html', 'http://avtoinsider.com/v-lnr-soobschili-chto-zaderzhali-ukrainskuyu-zhurnalistku/', 'http://vzglyadpenza.ru/2016/06/za-shpionazh-v-lnr-soobschili-o-zaderzhanii-ukrainskoy/', 'http://szaopressa.com/2016/06/22/rabotniki-gosbezopasnosti-lnr-zaderzhali-zhurnalistku-za.html', 'http://24science.ru/11294-savchenko-ustala-ot-takoy-zhizni.html', 'http://lastnews.com.ua/novosti-mira/515433-propavshego-v-karelii-malchika-nachali-iskat-v-lesu.html', 'http://kirov.monavista.ru/news/1757611/', 'http://e-gorlovka.com.ua/id/2016/kirovskie-narodnie-izbranniki-ne-dogovorilis-o-soveschanii-229116.html', 'http://kirov.monavista.ru/news/1757301/', 'http://kirov.monavista.ru/news/1757254/', 'http://vzglyadpenza.ru/2016/06/sud-arestoval-rukovoditelya-russkogo-avtorskogo-obschestva/', 'http://newsera.ru/2016/06/193894/obiski-v-russkom-avtorskom-obschestve-provodyatsya-po-delu.html', 'http://nash-sport.com/2016/06/28/yurista-evgenii-vasilevoy-arestovali-v-aeroportu-vnukovo.html', 'http://ryb.ru/2016/06/28/356345', 'http://newsler.info/217192-zhiteli-rf-zaderzhani-v-ispanii-po-podozreniyu-v-otmivanii', 'http://lastnews.com.ua/novosti-ukraini/524191-delo-russkoy-mafii-v-ispanii-zaderzhali-6-rossiyan-i-ukrainca.html', 'http://www.kasparov.ru/material.php?id=5772224A88215&section_id=43452BE8655FB', 'http://svodka.net/analitika/obozrenie/47247', 'http://kaliningrad.monavista.ru/news/1758247/', 'http://www.mk.ru/social/2016/06/28/zaderzhannogo-o-vnukovo-advokata-vasilevoy-otpustili.html', 'http://www.moscow-post.com/society/zaderzhan_advokat_evgenii_vasiljevoj21442/', 'http://newsler.info/217330-sbu-provela-obisk-u-harkovskoy-kommunistki-aleksandrovskoy', 'http://ryb.ru/2016/06/29/357003', 'http://mynewsonline24.ru/inopressa/135769-sbu-provela-obisk-u-eks-lidera-kommunisticheskoy-partii-harkova-alli-aleksandrovskoy.html', 'http://echospb.ru/2016/06/27/zamglavi-leyboristskoy-partii-uotson-prizval-uyti-v/', 'http://newsler.info/216758-v-britanii-podali-v-otstavku-sem-tenevih-ministrov', 'http://mynewsonline24.ru/inopressa/134296-uvolen-britanskiy-tenevoy-ministr-krizis-leyboristov.html', 'http://vladivostok.monavista.ru/news/1750611/', 'http://svodka.net/index.php?option=com_content&view=article&id=45900:da-ya-rabotal-v-usherb-sebe&catid=77:obozrenie', 'http://vladivostok.monavista.ru/news/1749309/', 'http://kaliningrad.monavista.ru/news/1758294/', 'http://szaopressa.com/2016/06/29/u-osnovnoy-kommunistki-harkovskoy-oblasti-sbu-provela-obisk.html', 'http://vladivostok.monavista.ru/news/1749142/', 'http://e-gorlovka.com.ua/id/2016/sbu-provelo-obisk-u-osnovnoy-harkovskoy-kommunistki-229556.html', 'http://mynewsonline24.ru/inopressa/135820-sbu-arestovala-rukovoditelya-kommunisticheskoy-partii-harkova-allu-aleksandrovskuyu.html', 'http://lastnews.com.ua/novosti-ukraini/524795-prokuratura-nazvala-prichiny-zaderzhki-aleksandrovskoy-podozrenie-obyavleno-i-ee-synu.html', 'http://mynewsonline24.ru/inopressa/135817-generalnaya-prokuratura-podtverdila-otstavku-brata-nikiti-belih.html', 'http://lastnews.com.ua/novosti-ukraini/524817-sbu-podozrevaet-aleksandrovskuyu-v-rabote-na-rossiyu.html']


def create_table(func, out_path):
    """create table with results of some algorithm which worked through function func"""
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open('corpus/readability_corpus.csv', 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            ind = 1
            for row in spamreader:
                if not row[0] in bad_links:
                    with open('corpus/docs/' + str(ind) + '.html', 'rb') as f:
                        text = f.read()
                        text = func(text)
                        row.append(text)
                        spamwriter.writerow(row)
                ind += 1

def create_table_with_confidence(func, out_path):
    """create table with results and confidences of some algorithm which worked through function func"""
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open('corpus/readability_corpus.csv', 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            ind = 1
            time = 0
            for row in spamreader:
                if not row[0] in bad_links:
                    title = row[2]
                    row = row[0:2]
                    print(row[0])
                    with open('corpus/docs/' + str(ind) + '.html', 'rb') as f:
                        text0 = f.read()
                        time1 = datetime.datetime.now()
                        text, confidence = func(text0, title)
                        delta = datetime.datetime.now()-time1
                        time += delta.total_seconds()
                        text1, confidence = func(text0, title, False)
                        row.append(text)
                        row.append(confidence)
                        row.append(text1)
                        spamwriter.writerow(row)
                ind += 1
            print("WORKING TIME: ", time)

def create_table_remote(func, out_path):
    """create table with results from remote pages"""
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open('corpus/readability_corpus.csv', 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if not row[0] in bad_links:
                    row = row[0:2]
                    row.append(func(row[0]))
                    print(row[0])
                    spamwriter.writerow(row)


def create_estimates_table(in_path, out_path):
    """create table with estimates of current algorithm (specified by in_path - path of csv table)"""
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open(in_path, 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                est1 = get_compare_estimate(row[1], row[2])
                est2 = get_compare_estimate(row[1], row[4])
                row.append(est1)
                row.append(est2)
                # print(row[3])
                spamwriter.writerow(row)
                if est1 < est2:
                    print("bad: ", row[0])
                elif est2 < est1:
                    print("good: ", row[0])


def get_final_estimate(in_path):
    """print final estimate of algorithm"""
    estimates = list()
    estimates1 = list()
    estimates90 = 0
    estimates100 = 0
    bads = 0
    confidence = 0
    with open(in_path, 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            #if not row[0] in cloudflare_links:
            if row[2] != 'ERROR':
                estim = float(row[len(row)-1])
                #estim2 = float(row[len(row)-2])
                if len(row) == 5:
                    confidence += float(row[3])
                # print(estim)
                estimates.append(estim)
                if estim >= 10:
                    estimates1.append(estim)
                else:
                    bads += 1
                    print(row[0])
                if estim >= 90:
                    estimates90 += 1
                if estim == 100:
                    estimates100 += 1
                #if estim2 > estim:
                #    print("GOOD CLEARING: "+row[0])
                #if estim > estim2:
                #    print("BAD CLEARING: "+row[0])
    print('Размер корпуса: ' + str(len(estimates)))
    print('Среднее: ' + str(float(sum(estimates))/len(estimates)))
    print('Среднее без плохих: ' + str(float(sum(estimates1))/len(estimates1)))
    print('Плохие: ' + str(bads*100/len(estimates)) + '%')
    print('Уверенность: ' + str(confidence*100/len(estimates)) + '%')
    print('>=90: ' + str(estimates90*100/len(estimates)) + '%')
    print('100: ' + str(estimates100*100/len(estimates)) + '%')

    estimates = list()
    estimates1 = list()
    estimates90 = 0
    estimates100 = 0
    bads = 0
    confidence = 0
    with open(in_path, 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            # if not row[0] in cloudflare_links:
            if row[2] != 'ERROR':
                estim = float(row[len(row) - 2])
                if len(row) == 5:
                    confidence += float(row[3])
                # print(estim)
                estimates.append(estim)
                if estim >= 10:
                    estimates1.append(estim)
                else:
                    bads += 1
                    print(row[0])
                if estim >= 90:
                    estimates90 += 1
                if estim == 100:
                    estimates100 += 1
    print('Размер корпуса: ' + str(len(estimates)))
    print('Среднее: ' + str(float(sum(estimates)) / len(estimates)))
    print('Среднее без плохих: ' + str(float(sum(estimates1)) / len(estimates1)))
    print('Плохие: ' + str(bads * 100 / len(estimates)) + '%')
    print('Уверенность: ' + str(confidence * 100 / len(estimates)) + '%')
    print('>=90: ' + str(estimates90 * 100 / len(estimates)) + '%')
    print('100: ' + str(estimates100 * 100 / len(estimates)) + '%')


def find_errors():
    """accessory function for finding errors"""
    with open('corpus/readability_lxml_estimates.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            if row[2] == 'ERROR':
                print(row[0])


def create_corpus():
    """creating local corpus by csv with links and ideal readability results"""
    with open('corpus/readability_corpus.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        ind = 1
        bads = []
        for row in spamreader:
            url = row[0]
            #if url != 'http://www.ntv.ru/novosti/1637696/':
            #    continue
            #print(url)
            try:
                #html_source = urllib.request.urlopen(url, timeout=10).read()
                html_source = send_get_request(url, has_encoding=True, gen_useragent=True)
                encoding = get_encoding(html_source) or 'utf-8'
                decoded_page = html_source.decode(encoding, 'replace')
                #print(decoded_page)
                estimate = get_compare_estimate(row[1], html.unescape(decoded_page))
                if estimate < 0.1:
                    #print(row[1])
                    print(url, "хрень", estimate, ind)
                    bads.append(url)
                    ind += 1
                    continue
                with open('corpus/docs/' + str(ind) + '.html', 'wb') as f:
                    f.write(html_source)
            except BaseException as err:
                if type(err) == HTTPError:
                    print(url, err.code)
                else:
                    print(url, type(err))
                bads.append(url)
                #if err is HTTPError:
                    #print(url, err.code)
            ind += 1
        print(bads)


if __name__ == '__main__':
    """start testing from here"""
    #with open('corpus/test.html', 'rb') as f:
    #with open('corpus/docs/272.html', 'rb') as f:
    #    html_source = f.read()
    #    text, confidence = read2.find_full_text(html_source, 'Глава РАО Сергей Федотов останется в СИЗО как минимум до…')
    #    print(text)
    #exit()
    url = 'http://daily.com.ua/http-daily-com-ua-newsfrompartners/1622192-boyepripasi-viyavili-v-avto-v-donetskiy-oblasti'
    html_source = send_get_request(url, has_encoding=True,
                                   gen_useragent=True)  # urllib.request.urlopen(url, timeout=10).read()
    # print(html_source.decode("utf-8"))
    text, confidence = read2.find_full_text(html_source)
    print(text)
    exit()
    """
    from readability.htmls import build_doc
    from lxml.html import HtmlElement

    html, encoding = build_doc(html_source)
    body = html.xpath("//body")[0]
    children = body.getchildren()
    # children = body.xpath("child::node()")
    for child in children:
        if type(child) == HtmlElement:
            print("tag", child.tag, child.get('class', ''))
            # if describe(elem) == '#content-area>div{04}':
            #    print(describe(child), child.tag, child_chars, child_tags, child_hyperchars, child_score)
            #    print(child.text_content())
        else:
            pass;
            # print("text",len(child))
            # print(len(child))
            # sum += len(child)#self.comp_score(len(child), 1, 0)
    exit()
    """
    """
    #url = 'http://36on.ru/news/criminal/65303-radi-zheny-voronezhets-na-chuzhom-dne-rozhdeniya-obchistil-seyf-s-zolotom-na-100-tysyach'
    #html_source = urllib.request.urlopen(url, timeout=10).read()
    #with open('corpus/docs/' + str(75) + '.html', 'rb') as f:
    #    html_source = f.read()
    #print(read2.find_full_text(html_source))
    #exit()

    create_corpus()
    """
    #estimate_estimate()
    #print(len(bad_links))
    create_table_with_confidence(read2.find_full_text, 'corpus/read2.csv')
    create_estimates_table('corpus/read2.csv', 'corpus/read2_estimates.csv')
    print('Алгоритм readability fusion')
    get_final_estimate('corpus/read2_estimates.csv')
    exit()

    #create_table(kingwkb.find_full_text().find_full_text, 'corpus/kingwkb.csv')
    #create_estimates_table('corpus/kingwkb.csv', 'corpus/kingwkb_estimates.csv')
    #print('Алгоритм kingwkb-readability')
    #get_final_estimate('corpus/kingwkb_estimates.csv')

    #create_table(bread.find_full_text, 'corpus/breadability.csv')
    #create_estimates_table('corpus/breadability.csv', 'corpus/breadability_estimates.csv')
    #print('Алгоритм breadability')
    #get_final_estimate('corpus/breadability_estimates.csv')

    #create_table(read_lxml.find_full_text, 'corpus/readability_lxml.csv')
    #create_estimates_table('corpus/readability_lxml.csv', 'corpus/readability_lxml_estimates.csv')
    print('Алгоритм lxml-readability')
    get_final_estimate('corpus/readability_lxml_estimates.csv')

    #create_table_remote(read_com.find_full_text, 'corpus/readability_com.csv')
    #create_estimates_table('corpus/readability_com.csv', 'corpus/readability_com_estimates.csv')
    #print('Алгоритм readability.com')
    #get_final_estimate('corpus/readability_com_estimates.csv')


    #print(read_com.find_full_text('http://www.moscow-post.com/news/society/vitse-premjer_karelii_popal_pod_podozrenie94812/'))
    #find_errors()



# select guid from documents where source_id='71dc5343-c27d-44bf-aa76-f4d8085317fe' order by created asc