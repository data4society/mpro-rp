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

# links whick blocked by cloudflare firewall
cloudflare_links = ['http://podrobnosti.ua/2115445-frantsuzy-edut-rassledovat-zaderzhanie-sbu-terrorista.html', 'http://ryb.ru/2016/06/21/348972',
    'http://ryb.ru/2016/06/21/348890', 'http://ryb.ru/2016/06/21/349088',
    'http://www.aysor.am/ru/news/2016/06/21/%D1%81%D0%B5%D1%84%D0%B8%D0%BB%D1%8F%D0%BD/1100847',
    'http://news.am/rus/news/333253.html',
    'http://news.am/rus/news/333232.html',
    'http://news.am/rus/news/333247.html',
    'http://u-f.ru/News/politics/u9/2016/06/18/101730',
    'http://newsday24.org/11294-savchenko-ustala-ot-takoy-zhizni.html']

bad_links = ['http://pskov.riasv.ru/news/vo_frantsii_arestovali_krupnogo_pskovskogo_zemlevl/1110912/', 'http://podrobnosti.ua/2115445-frantsuzy-edut-rassledovat-zaderzhanie-sbu-terrorista.html', 'http://poliksal.ru/novosti-v-mire/45953-savchenko-prizvala-zapad-ostanovit-rossiyu-na-ukrainskoy-granice.html', 'http://ryb.ru/2016/06/21/348972', 'http://ryb.ru/2016/06/21/348890', 'http://ryb.ru/2016/06/21/349088', 'http://poliksal.ru/novosti-rosii/45899-novye-shokiruyuschie-zayavleniya-savchenko-ona-rasskazala-miru-o-planah-kremlya-zavoevat-evropu.html', 'http://poliksal.ru/novosti-v-mire/45894-v-strasburge-savchenko-prizvala-evropu-dressirovat-rossiyu.html', 'http://www.aysor.am/ru/news/2016/06/21/%D1%81%D0%B5%D1%84%D0%B8%D0%BB%D1%8F%D0%BD/1100847', 'http://news.am/rus/news/333253.html', 'http://lratvakan.com/news/212802.html', 'http://news.am/rus/news/333232.html', 'http://news.am/rus/news/333247.html', 'http://u-f.ru/News/politics/u9/2016/06/18/101730', 'http://newsday24.org/11294-savchenko-ustala-ot-takoy-zhizni.html', 'http://replyua.net/news/politika-v-mire/31892-nadezhda-savchenko-uspeshno-sdala-test-na-politicheskoy-scene.html', 'http://bk55.ru/news/article/77109/', 'http://blagoveshensk.riasv.ru/news/pogibshie_na_syamozere_deti_ne_znali_kak_pravilno_/1111499/', 'http://petrozavodsk.riasv.ru/news/k_gibeli_shkolnikov_v_karelii_mogut_bit_prichastni/1111543/', 'http://kirov.monavista.ru/news/1757611/', 'http://govoritmoskva.ru/news/84017/', 'http://kirov.monavista.ru/news/1757301/', 'http://kirov.monavista.ru/news/1757254/', 'http://vologda.riasv.ru/news/pochemu_gendirektor_rao_fedotov_pered_arestom_poda/1132927/', 'http://ryb.ru/2016/06/28/356345', 'http://murmansk.riasv.ru/news/v_murmanskoy_oblasti_politseyskie_zaderzhali_napav/1128687/', 'http://murmansk.riasv.ru/news/segodnya_v_umvd_rossii_po_murmanskoy_oblasti_nagra/1127565/', 'http://www.kasparov.ru/material.php?id=5772224A88215&section_id=43452BE8655FB', 'http://shkvarki.org/za-rubezhem/item/8297-v-tsentre-mogileva-militsiya-razognala-detskij-prazdnik-a-organizatorov-zabrala-v-otdelenie', 'http://naviny.by/rubrics/disaster/2016/06/28/ic_news_124_477382/', 'http://euroradio.fm/ru/mogilevskaya-miliciya-prokommentirovala-zaderzhanie-organizatora-detskogo-prazdnika', 'http://naviny.by/rubrics/disaster/2016/06/27/ic_news_124_477354/', 'https://charter97.org/ru/news/2016/6/27/210893/', 'https://charter97.org/ru/news/2016/6/27/210823/', 'http://ijevsk.jjew.ru/news/zashchita_obzhalovala_arest_gubernatora_kirovskoy_/1149958/', 'http://rostovnadonu.riasv.ru/news/gendirektora_rossiyskogo_avtorskogo_obshchestva_po/1133686/', 'http://kaliningrad.monavista.ru/news/1758247/', 'http://gigamir.net/money/economics/pub2671949', 'http://www.mk.ru/social/2016/06/28/zaderzhannogo-o-vnukovo-advokata-vasilevoy-otpustili.html', 'http://ryb.ru/2016/06/29/357003', 'http://newsler.info/216758-v-britanii-podali-v-otstavku-sem-tenevih-ministrov', 'http://mk-london.co.uk/news/u489/2016/06/27/13494', 'https://meduza.io/feature/2016/06/27/brekzit-posledstviya', 'http://vladivostok.monavista.ru/news/1750611/', 'http://vladivostok.monavista.ru/news/1749309/', 'http://kaliningrad.monavista.ru/news/1758294/', 'http://vladivostok.monavista.ru/news/1749142/', 'http://poliksal.ru/proishestviya/47611-nikita-belyh-prodolzhaet-golodovku-i-zayavlyaet-o-podstave-pochemu-gubernator-uporno-ne-priznaetsya-vo-vzyatkah.html', 'http://w-n.com.ua/archives/4181']


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
            for row in spamreader:
                if not row[0] in bad_links:
                    with open('corpus/docs/' + str(ind) + '.html', 'rb') as f:
                        text0 = f.read()
                        text, confidence = func(text0)
                        text1, confidence = func(text0, '', False)
                        row.append(text)
                        row.append(confidence)
                        row.append(text1)
                        spamwriter.writerow(row)
                ind += 1

def create_table_remote(func, out_path):
    """create table with results from remote pages"""
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
    """create table with estimates of current algorithm (specified by in_path - path of csv table)"""
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open(in_path, 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                row.append(get_compare_estimate(row[1],row[2]))
                row.append(get_compare_estimate(row[1],row[4]))
                # print(row[3])
                spamwriter.writerow(row)


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
                estim2 = float(row[len(row)-2])
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
                if estim2 > estim:
                    print("GOOD CLEARING: "+row[0])
                if estim > estim2:
                    print("BAD CLEARING: "+row[0])
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
    """start testing from here"""
    """
    with open('corpus/test.html', 'rb') as f:
        html_source = f.read()
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
    #url = 'http://www.gazeta.kg/news/important/99343-sud-arestoval-rukovoditeley-lagerya-na-syamozere.html'
    #html_source = urllib.request.urlopen(url, timeout=10).read()
    #with open('corpus/docs/' + str(75) + '.html', 'rb') as f:
    #    html_source = f.read()
    #print(read2.find_full_text(html_source))
    #exit()

    # create_corpus()
    # exit()
    #estimate_estimate()
    #print(len(bad_links))
    create_table_with_confidence(read2.find_full_text, 'corpus/read2.csv')
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

    #create_table(read_lxml.find_full_text, 'corpus/readability_lxml.csv')
    #create_estimates_table('corpus/readability_lxml.csv', 'corpus/readability_lxml_estimates.csv')
    #print('Алгоритм lxml-readability')
    #get_final_estimate('corpus/readability_lxml_estimates.csv')

    #create_table_remote(read_com.find_full_text, 'corpus/readability_com.csv')
    #create_estimates_table('corpus/readability_com.csv', 'corpus/readability_com_estimates.csv')
    #print('Алгоритм readability.com')
    #get_final_estimate('corpus/readability_com_estimates.csv')


    #print(read_com.find_full_text('http://www.moscow-post.com/news/society/vitse-premjer_karelii_popal_pod_podozrenie94812/'))
    #find_errors()



# select guid from documents where source_id='71dc5343-c27d-44bf-aa76-f4d8085317fe' order by created asc