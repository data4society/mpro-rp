"""script for testing algorithms"""
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


cloudflare_links = ['http://podrobnosti.ua/2115445-frantsuzy-edut-rassledovat-zaderzhanie-sbu-terrorista.html', 'http://ryb.ru/2016/06/21/348972',
    'http://ryb.ru/2016/06/21/348890', 'http://ryb.ru/2016/06/21/349088',
    'http://www.aysor.am/ru/news/2016/06/21/%D1%81%D0%B5%D1%84%D0%B8%D0%BB%D1%8F%D0%BD/1100847',
    'http://news.am/rus/news/333253.html',
    'http://news.am/rus/news/333232.html',
    'http://news.am/rus/news/333247.html',
    'http://u-f.ru/News/politics/u9/2016/06/18/101730',
    'http://newsday24.org/11294-savchenko-ustala-ot-takoy-zhizni.html']

bad_links = ['http://pskov.riasv.ru/news/vo_frantsii_arestovali_krupnogo_pskovskogo_zemlevl/1110912/', 'http://news-russia.info/2016/06/21/gricak-kosvenno-priznal-chto-lager-dzhihadistov-mog-zhit-v/', 'http://podrobnosti.ua/2115445-frantsuzy-edut-rassledovat-zaderzhanie-sbu-terrorista.html', 'http://poliksal.ru/novosti-v-mire/45953-savchenko-prizvala-zapad-ostanovit-rossiyu-na-ukrainskoy-granice.html', 'http://ryb.ru/2016/06/21/348972', 'http://ryb.ru/2016/06/21/348890', 'http://ryb.ru/2016/06/21/349088', 'http://lastnews.com.ua/novosti-ukraini/515506-ne-zhelayu-nikomu-imet-takogo-soseda-kak-rossiya.html', 'http://poliksal.ru/novosti-rosii/45899-novye-shokiruyuschie-zayavleniya-savchenko-ona-rasskazala-miru-o-planah-kremlya-zavoevat-evropu.html', 'http://poliksal.ru/novosti-v-mire/45894-v-strasburge-savchenko-prizvala-evropu-dressirovat-rossiyu.html', 'http://news-russia.info/2016/06/21/v-plen-terroristov-lnr-ugodila-ukrainskaya-zhurnalistka/', 'http://www.aysor.am/ru/news/2016/06/21/%D1%81%D0%B5%D1%84%D0%B8%D0%BB%D1%8F%D0%BD/1100847', 'http://news.am/rus/news/333253.html', 'http://lratvakan.com/news/212802.html', 'http://news.am/rus/news/333232.html', 'http://news.am/rus/news/333247.html', 'http://u-f.ru/News/politics/u9/2016/06/18/101730', 'http://news-russia.info/2016/06/21/v-ukraine-net-baz-podgotovki-dzhihadistov-gricak/', 'http://newsday24.org/11294-savchenko-ustala-ot-takoy-zhizni.html']


def create_table(func, out_path):
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


def create_table_remote(func, out_path):
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open('corpus/readability_corpus.csv', 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if not row[0] in bad_links:
                    row.append(func(row[0]))
                    print(row[0])
                    spamwriter.writerow(row)


def create_estimates_table(in_path, out_path):
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open(in_path, 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                row.append(get_compare_estimate(row[1],row[2]))
                # print(row[3])
                spamwriter.writerow(row)


def get_final_estimate(in_path):
    estimates = list()
    estimates1 = list()
    estimates90 = 0
    estimates100 = 0
    bads = 0
    with open(in_path, 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            #if not row[0] in cloudflare_links:
            if row[2] != 'ERROR':
                estim = float(row[3])
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
    print('Среднее: ' + str(float(sum(estimates))/len(estimates)))
    print('Среднее без плохих: ' + str(float(sum(estimates1))/len(estimates1)))
    print('Плохие: ' + str(bads*100/len(estimates)) + '%')
    print('>=90: ' + str(estimates90*100/len(estimates)) + '%')
    print('100: ' + str(estimates100*100/len(estimates)) + '%')


def find_errors():
    with open('corpus/readability_lxml_estimates.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            if row[2] == 'ERROR':
                print(row[0])


def estimate_estimate():
    with open('corpus/readability_lxml_estimates.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile)

        for row in spamreader:
            if row[0] == 'http://echospb.ru/2016/06/22/v-sb-ukraini-soobschili-chto-v-gosudarstve-net-baz-po/':
                source = row[1]
                #source = strip_tags(source)
                source = to_plain_text(source)
                res = read_lxml.find_full_text('http://echospb.ru/2016/06/22/v-sb-ukraini-soobschili-chto-v-gosudarstve-net-baz-po/')
                print(source)
                print(res)
                print(get_compare_estimate(source,res))


def create_corpus():
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
                html_source = urllib.request.urlopen(url, timeout=10).read()
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
    """
    with open('corpus/test.html', 'rb') as f:
        html_source = f.read()
    from readability.htmls import build_doc
    from lxml.html import HtmlElement
    html, encoding = build_doc(html_source)
    body = html.xpath("//body")[0]
    children = body.getchildren()
    #children = body.xpath("child::node()")
    for child in children:
        if type(child) == HtmlElement:
            print("tag",child.tag, child.get('class', ''))
            # if describe(elem) == '#content-area>div{04}':
            #    print(describe(child), child.tag, child_chars, child_tags, child_hyperchars, child_score)
            #    print(child.text_content())
        else:
            pass;
            #print("text",len(child))
            # print(len(child))
            # sum += len(child)#self.comp_score(len(child), 1, 0)
    exit()
    """
    #url = 'http://www.gazeta.kg/news/important/99343-sud-arestoval-rukovoditeley-lagerya-na-syamozere.html'
    #html_source = urllib.request.urlopen(url, timeout=10).read()
    #with open('corpus/docs/' + str(68) + '.html', 'rb') as f:
    #    html_source = f.read()
    #print(read2.find_full_text(html_source))
    #exit()

    #create_corpus()
    #exit()
    #estimate_estimate()

    create_table(read2.find_full_text, 'corpus/read2.csv')
    create_estimates_table('corpus/read2.csv', 'corpus/read2_estimates.csv')
    print('Алгоритм readability2')
    get_final_estimate('corpus/read2_estimates.csv')

    #create_table(kingwkb.find_full_text().find_full_text, 'corpus/kingwkb.csv')
    #create_estimates_table('corpus/kingwkb.csv', 'corpus/kingwkb_estimates.csv')
    #print('Алгоритм kingwkb-readability')
    #get_final_estimate('corpus/kingwkb_estimates.csv')

    #create_table(bread.find_full_text, 'corpus/breadability.csv')
    #create_estimates_table('corpus/breadability.csv', 'corpus/breadability_estimates.csv')
    #print('Алгоритм breadability')
    #get_final_estimate('corpus/breadability_estimates.csv')

    create_table(read_lxml.find_full_text, 'corpus/readability_lxml.csv')
    create_estimates_table('corpus/readability_lxml.csv', 'corpus/readability_lxml_estimates.csv')
    print('Алгоритм lxml-readability')
    get_final_estimate('corpus/readability_lxml_estimates.csv')

    #create_table_remote(read_com.find_full_text, 'corpus/readability_com.csv')
    #create_estimates_table('corpus/readability_com.csv', 'corpus/readability_com_estimates.csv')
    #print('Алгоритм readability.com')
    #get_final_estimate('corpus/readability_com_estimates.csv')


    #print(read_com.find_full_text('http://www.moscow-post.com/news/society/vitse-premjer_karelii_popal_pod_podozrenie94812/'))
    #find_errors()

