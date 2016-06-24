"""script for testing algorithms"""
import mprorp.crawler.readability.readability_com as read_com
import mprorp.crawler.readability.lxml_readability as read_lxml
import csv
from mprorp.crawler.readability.shingling import get_compare_estimate

def create_table(func, out_path):
    with open(out_path, 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open('corpus/readability_corpus.csv', 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
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
                print(row[3])
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
            estim = float(row[3])
            # print(estim)
            estimates.append(estim)
            if estim >= 10:
                estimates1.append(estim)
            else:
                bads += 1
            if estim >= 90:
                estimates90 += 1
            if estim == 100:
                estimates100 += 1
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


if __name__ == '__main__':
    links = ['http://podrobnosti.ua/2115445-frantsuzy-edut-rassledovat-zaderzhanie-sbu-terrorista.html', 'http://ryb.ru/2016/06/21/348972',
    'http://ryb.ru/2016/06/21/348890', 'http://ryb.ru/2016/06/21/349088',
    'http://www.aysor.am/ru/news/2016/06/21/%D1%81%D0%B5%D1%84%D0%B8%D0%BB%D1%8F%D0%BD/1100847',
    'http://news.am/rus/news/333253.html',
    'http://news.am/rus/news/333232.html',
    'http://news.am/rus/news/333247.html',
    'http://u-f.ru/News/politics/u9/2016/06/18/101730',
    'http://newsday24.org/11294-savchenko-ustala-ot-takoy-zhizni.html']
    for link in links:
        print(read_lxml.find_full_text(link))
    #create_table(read_com.find_full_text, 'corpus/readability_com.csv')
    #create_estimates_table('corpus/readability_com.csv', 'corpus/readability_com_estimates.csv')
    #print('Алгоритм readability.com')
    #get_final_estimate('corpus/readability_com_estimates.csv')

    #create_table(read_lxml.find_full_text, 'corpus/readability_lxml.csv')
    #create_estimates_table('corpus/readability_lxml.csv', 'corpus/readability_lxml_estimates.csv')
    #print('Алгоритм lxml-readability')
    #get_final_estimate('corpus/readability_lxml_estimates.csv')
    # print(read_com.find_full_text('http://www.moscow-post.com/news/society/vitse-premjer_karelii_popal_pod_podozrenie94812/'))
    #find_errors()
