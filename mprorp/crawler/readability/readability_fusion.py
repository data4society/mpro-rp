"""readability algorithm which is fusion of lxml-readability and readability2"""
from __future__ import print_function
import logging
import re
import sys
import math

import html
from collections import defaultdict
from lxml.etree import tostring
from lxml.etree import tounicode
from lxml.html import document_fromstring
from lxml.html import fragment_fromstring

from readability.cleaners import clean_attributes
from readability.cleaners import html_cleaner
from readability.htmls import build_doc
from readability.htmls import get_body
from readability.htmls import get_title
from readability.htmls import shorten_title
from readability.compat import str_
from readability.debug import describe, text_content
from lxml.html import HtmlElement
from lxml import etree

# from mprorp.analyzer.pymystem3_w import Mystem
from mprorp.controller.init import global_mystem as mystem
from mprorp.crawler.utils import to_plain_text
from mprorp.crawler.readability.shingling import get_compare_estimate

from mprorp.utils import levenshtein_norm_distance


log = logging.getLogger("readability.readability")

REGEXES = {
    'unlikelyCandidatesRe': re.compile('combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter|podval|adsbygoogle|share|uptolike-buttons|error|adfox_banner', re.I),
    'okMaybeItsACandidateRe': re.compile('and|article|body|column|main|shadow|js-pagination', re.I),
    'positiveRe': re.compile('article|body|content|entry|hentry|main|page|pagination|post|text|blog|story', re.I),
    'negativeRe': re.compile('combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget', re.I),
    'divToPElementsRe': re.compile('<(blockquote|dl|div|img|ol|p|pre|table|ul)', re.I),  #re.compile('<(a|blockquote|dl|div|img|ol|p|pre|table|ul)', re.I),
    'rfBadContent': re.compile('footer|textarea|comment', re.I),
    'rfBadStart': re.compile('Метки:|Рубрики:|Новости партнеров|Просмотров:|Темы:|Loading', re.I),
    'rfBadStartWithLink': re.compile('Читайте|Пишите|Смотрите|Подробнее читайте|Подписывайтесь|Читать дальше|Хотите поделиться|Подпишитесь|Следите за', re.I),
    'rfBadSearch': re.compile('Ctrl\+Enter', re.I),
    'rfBadSearchWithLink': re.compile('Подписывайтесь на наш', re.I),

    #'replaceBrsRe': re.compile('(<br[^>]*>[ \n\r\t]*){2,}',re.I),
    #'replaceFontsRe': re.compile('<(\/?)font[^>]*>',re.I),
    #'trimRe': re.compile('^\s+|\s+$/'),
    #'normalizeRe': re.compile('\s{2,}/'),
    #'killBreaksRe': re.compile('(<br\s*\/?>(\s|&nbsp;?)*){1,}/'),
    'videoRe': re.compile('https?:\/\/(www\.)?(youtube|vimeo)\.com', re.I),
    #skipFootnoteLink:      /^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$/i,
}
THRESHOLD_RATIO = 0.1# ++++++++0.666
TITLE_DENSITY_THRESHOLD = 0.005
MAX_TITLE_CHECKING = 10
#mystem = Mystem()
#mystem.start()
print("READABILITY FUSION INIT MYSTEM")


class Unparseable(ValueError):
    pass


def to_int(x):
    if not x:
        return None
    x = x.strip()
    if x.endswith('px'):
        return int(x[:-2])
    if x.endswith('em'):
        return int(x[:-2]) * 12
    return int(x)


def clean(text):
    text = re.sub('\s*\n\s*', '\n', text)
    text = re.sub('\t|[ \t]{2,}', ' ', text)
    return text.strip()


def text_length(i):
    return len(clean(i.text_content() or ""))

regexp_type = type(re.compile('hello, world'))

def compile_pattern(elements):
    if not elements:
        return None
    elif isinstance(elements, (list, tuple)):
        return list(elements)
    elif isinstance(elements, regexp_type):
        return elements
    else:
        # assume string or string like object
        elements = elements.split(',')
        return re.compile(u'|'.join([re.escape(x.lower()) for x in elements]), re.U)

class Document:
    """Class to build a etree document out of html."""

    def __init__(self, input, positive_keywords=None, negative_keywords=None,
                 url=None, min_text_length=25, retry_length=250, xpath=False):
        """Generate the document

        :param input: string of the html content.
        :param positive_keywords: regex or list of patterns in classes and ids
        :param negative_keywords: regex or list of patterns in classes and ids
        :param min_text_length:
        :param retry_length:

        Example:
            positive_keywords=["news-item", "block"]
            negative_keywords=["mysidebar", "related", "ads"]
        """
        self.input = input
        self.html = None
        self.encoding = None
        self.positive_keywords = compile_pattern(positive_keywords)
        self.negative_keywords = compile_pattern(negative_keywords)
        self.url = url
        self.min_text_length = min_text_length
        self.retry_length = retry_length
        self.xpath = xpath
        self.confidence = -1

    def _html(self, force=False):
        if force or self.html is None:
            #print(html.unescape(self.input.decode("utf-8")))
            self.html = self._parse(self.input)
            if self.xpath:
                root = self.html.getroottree()
                for i in self.html.getiterator():
                    #print root.getpath(i)
                    i.attrib['x'] = root.getpath(i)
        return self.html

    def _parse(self, input):
        doc, self.encoding = build_doc(input)
        doc = html_cleaner.clean_html(doc)
        base_href = self.url
        if base_href:
            # trying to guard against bad links like <a href="http://[http://...">
            try:
                # such support is added in lxml 3.3.0
                doc.make_links_absolute(base_href, resolve_base_href=True, handle_failures='discard')
            except TypeError: #make_links_absolute() got an unexpected keyword argument 'handle_failures'
                # then we have lxml < 3.3.0
                # please upgrade to lxml >= 3.3.0 if you're failing here!
                doc.make_links_absolute(base_href, resolve_base_href=True)
        else:
            doc.resolve_base_href()
        return doc

    def content(self):
        return get_body(self._html(True))

    def title(self):
        return get_title(self._html(True))

    def short_title(self):
        return shorten_title(self._html(False))

    def get_clean_html(self):
         return clean_attributes(tounicode(self.html))

    def summary(self, html_partial=False, title='', fusion_clearing = True):
        """Generate the summary of the html docuemnt

        :param html_partial: return only the div of the document, don't wrap
        in html and body tags.

        :param title: title of page.

        """

        try:
            ruthless = True
            while True:
                self._html(True)
                #print(html.unescape(etree.tostring(self.html, pretty_print=True).decode("utf-8")))
                #exit()
                self.title_text = ''
                #if title == '':
                #    h1 = self.html.find(".//h1")
                #    if h1 != None:
                #        self.title_text = h1.text_content()
                #else:
                #    self.title_text = title
                self.title_text = self.short_title()  # self.html.find(".//title").text_content()  #self.title()
                if self.title_text == '':
                    h1 = self.html.find(".//h1")
                    if h1 != None:
                        self.title_text = h1.text_content()
                if title != '':
                    if levenshtein_norm_distance(self.title_text, title) > 0.5:
                        self.title_text = title
                self.title_text = to_plain_text(self.title_text)
                self.title_lemmas = mystem.lemmatize(self.title_text)
                #mystem.close()
                self.title_lemmas = [word for word in self.title_lemmas if len(word.strip())>2]
                meta = dict()
                metatag = self.html.find(".//title")
                if metatag is not None:
                    meta["title"] = metatag.text_content()
                metatag = self.html.find(".//meta[@name='abstract']")
                if metatag is not None:
                    meta["abstract"] = metatag.get('content', '')
                metatag = self.html.find(".//meta[@name='author']")
                if metatag is not None:
                    meta["author"] = metatag.get('content', '')
                metatag = self.html.find(".//meta[@name='description']")
                if metatag is not None:
                    meta["description"] = metatag.get('content', '')
                metatag = self.html.find(".//meta[@name='keywords']")
                if metatag is not None:
                    meta["keywords"] = metatag.get('content', '')
                self.meta = meta
                for i in self.tags(self.html, 'script', 'style'):
                    i.drop_tree()
                for i in self.tags(self.html, 'body'):
                    i.set('id', 'readabilityBody')
                if ruthless:
                    self.remove_unlikely_candidates()
                self.transform_misused_divs_into_paragraphs()
                #print(html.unescape(etree.tostring(self.html, pretty_print=True).decode("utf-8")))
                #exit()
                #candidates = self.score_paragraphs()

                #best_candidate = self.select_best_candidate(candidates)


                candidates = {}
                res = {
                    'sum': 0,
                    'node': None
                }
                self.compute(self.html, res, candidates)
                best_candidate = self.select_best_candidate(candidates)
                #print(res)

                if best_candidate:
                    article = self.get_article(candidates, best_candidate,
                            html_partial=html_partial)
                else:
                    if ruthless:
                        #log.info("ruthless removal did not work. ")
                        ruthless = False
                        #log.debug("ended up stripping too much - going for a safer _parse")
                        # try again
                        continue
                    else:
                        #log.debug("Ruthless and lenient parsing did not work. Returning raw html")
                        article = self.html.find('body')
                        if article is None:
                            article = self.html
                #print(html.unescape(etree.tostring(article, pretty_print=True).decode("utf-8")))
                #exit()
                cleaned_article = self.sanitize(article, candidates, fusion_clearing)

                article_length = len(cleaned_article or '')
                retry_length = self.retry_length
                of_acceptable_length = article_length >= retry_length
                if ruthless and not of_acceptable_length:
                    ruthless = False
                    # Loop through and try again.
                    continue
                else:
                    return cleaned_article, self.title_text, self.meta
        except Exception as e:
            log.exception('error getting summary: ')
            if sys.version_info[0] == 2:
                from readability.compat.two import raise_with_traceback
            else:
                from readability.compat.three import raise_with_traceback
            raise_with_traceback(Unparseable, sys.exc_info()[2], str_(e))
        #mystem.close()

    def get_article(self, candidates, best_candidate, html_partial=False, with_siblings=True):
        # Now that we have the top candidate, look through its siblings for
        # content that might also be related.
        # Things like preambles, content split by ads that we removed, etc.
        if html_partial:
            output = fragment_fromstring('<div/>')
        else:
            output = document_fromstring('<div/>')
        best_elem = best_candidate['elem']
        if with_siblings:
            sibling_score_threshold = max([
                10,
                best_candidate['content_score'] * 0.2])
            # create a new html document with a html->body->div
            parent = best_elem.getparent()
            siblings = parent.getchildren() if parent is not None else [best_elem]
            for sibling in siblings:
                # in lxml there no concept of simple text
                # if isinstance(sibling, NavigableString): continue
                append = False
                if sibling is best_elem:
                    append = True
                sibling_key = sibling  # HashableElement(sibling)
                if sibling_key in candidates and \
                    candidates[sibling_key]['content_score'] >= sibling_score_threshold:
                    append = True

                if sibling.tag == "p":
                    link_density = self.get_link_density(sibling)
                    node_content = sibling.text or ""
                    node_length = len(node_content)

                    if node_length > 80 and link_density < 0.25:
                        append = True
                    elif node_length <= 80 \
                        and link_density == 0 \
                        and re.search('\.( |$)', node_content):
                        append = True
                #append = False
                if append:
                    # We don't want to append directly to output, but the div
                    # in html->body->div
                    if html_partial:
                        output.append(sibling)
                    else:
                        output.getchildren()[0].getchildren()[0].append(sibling)
        #if output is not None:
        #    output.append(best_elem)
        else:
            if html_partial:
                output.append(best_elem)
            else:
                output.getchildren()[0].getchildren()[0].append(best_elem)
        return output


    def compute(self, elem, res, candidates, linked=False):
        chars = 0
        tags = 1
        hyperchars = 0
        sum = 0

        linked = linked or (elem.tag in ['button','a','option'])
        #children = elem.getchildren()
        children = elem.xpath("child::node()")
        for child in children:
            if isinstance(child, HtmlElement):
                child_chars, child_tags, child_hyperchars, child_score = self.compute(child, res, candidates, linked)
                chars += child_chars
                tags += child_tags
                hyperchars += child_hyperchars
                sum += child_score
                #if describe(elem) == '.article_body>.text':
                #    print(child_score)
                #if describe(elem) == 'html>body#readabilityBody':
                #print(describe(elem), describe(child), child.tag, child_chars, child_tags, child_hyperchars, child_score)
                #print(child.text_content())
            else:
                #print(len(child))
                child = str(child).strip()
                child_text_len = len(child)
                sum += child_text_len
                #sum += self.comp_score(child_text_len, 1, 0)
                chars += child_text_len
                #if describe(elem) == 'p.bottom>span.summary':
                #    print(child_text_len)
                #print(child)

        #if describe(elem) == 'div{04}>p{08}':
        #    print(elem.xpath(".//*"))
        #    print(elem.tail,elem.text)
        #if len(children) == 1:
        #    chars = text_length(elem)
        if linked:
            hyperchars = chars
            #print("AAAAAAA", elem.tag, describe(elem))
        #chars_of_text_blocks = text_length(elem)-chars
        #sum += self.comp_score(chars_of_text_blocks, 1, 0)


        score = self.comp_score(chars, tags, hyperchars)
        #if describe(elem) == '.static>p{04}':
        #print(describe(elem), chars, tags, hyperchars, score, sum)
        #print(elem.text_content())
        #if describe(elem) == 'article.item>h3.article_subheader':
        #    print(elem.text_content())
        #    exit()

        s = "%s %s %s" % (elem.get('class', ''), elem.get('id', ''), elem.tag)
        if REGEXES['rfBadContent'].search(s):
            sum = 0.1 * sum

        candidates[elem] = {
            'content_score': sum,
            'elem': elem
        }
        #print(describe(elem),sum)
        if sum > res['sum']:
            res['node'] = elem
            res['sum'] = sum

        return chars, tags, hyperchars, score

    def comp_score(self, chars, tags, hyperchars):
        return (chars / tags) * (1-(hyperchars + 1)/(chars + 1)) #math.log2((chars + 1) / (hyperchars + 1))

    def get_confidence(self):
        if self.confidence == -1:
            self.summary()
        return self.confidence

    def select_best_candidate(self, candidates):
        if not candidates:
            return None

        sorted_candidates = sorted(
            candidates.values(),
            key=lambda x: x['content_score'],
            reverse=True
        )
        #for candidate in sorted_candidates[:5]:
            #elem = candidate['elem']
            #log.info("Top 5 : %6.3f %s" % (candidate['content_score'],describe(elem)))
            #print("BEST",describe(elem),candidate['content_score'])

        best_candidate = sorted_candidates[0]
        best_candidate_score = best_candidate['content_score']
        if best_candidate_score > 0:
            n = 0
            for candidate in sorted_candidates:
                if candidate['content_score']/best_candidate_score < THRESHOLD_RATIO or n == MAX_TITLE_CHECKING:
                    break;
                n += 1
        if n == 1:
            self.confidence = 1
        else:
            best_candidates = sorted_candidates[:n]
            best_final_score = -1
            for candidate in best_candidates:
                elem = candidate['elem']
                strate = self.score_title_rate(elem)
                if strate > TITLE_DENSITY_THRESHOLD:
                    best_candidate = candidate
                    break
                # print("BEST", describe(elem), candidate['content_score'], strate)
                final_score = strate*candidate['content_score']
                if final_score>best_final_score:
                    best_final_score = final_score
                    best_candidate = candidate
                #from mprorp.crawler.readability.shingling import get_compare_estimate
                #print(get_compare_estimate(, title)
            #print(title)
            if best_candidate['content_score']:
                self.confidence = 1-sorted_candidates[1]['content_score']/best_candidate['content_score']

        return best_candidate


    def get_link_density(self, elem):
        link_length = 0
        for i in elem.findall(".//a"):
            link_length += text_length(i)
        #if len(elem.findall(".//div") or elem.findall(".//p")):
        #    link_length = link_length
        total_length = text_length(elem)
        return float(link_length) / max(total_length, 1)


    def class_weight(self, e):
        weight = 0
        for feature in [e.get('class', None), e.get('id', None)]:
            if feature:
                if REGEXES['negativeRe'].search(feature):
                    weight -= 25

                if REGEXES['positiveRe'].search(feature):
                    weight += 25

                if self.positive_keywords and self.positive_keywords.search(feature):
                    weight += 25

                if self.negative_keywords and self.negative_keywords.search(feature):
                    weight -= 25

        if self.positive_keywords and self.positive_keywords.match('tag-'+e.tag):
            weight += 25

        if self.negative_keywords and self.negative_keywords.match('tag-'+e.tag):
            weight -= 25

        return weight

    def score_tag(self, elem):
        chars = text_length(elem)

        hyperchars = 0
        for i in elem.findall(".//a"):
            hyperchars += text_length(i)
        for i in elem.findall(".//button"):
            hyperchars += text_length(i)
        for i in elem.findall(".//option"):
            hyperchars += text_length(i)
        tags = elem.xpath('count(.//*)') + 1
        #print(describe(elem))
        #print(chars, hyperchars, tags)

        score = (chars / tags) * math.log2((chars + 1) / (hyperchars + 1))
        return score


    def remove_unlikely_candidates(self):
        #print(etree.tostring(self.html, pretty_print=True))
        #print(self.html.xpath("//div[@class='newstext']"))
        #print(self.html.xpath('count(.//*)'))
        ind = 0
        elements_to_drop = []
        for elem in self.html.iter():
            ind += 1
            s = "%s %s" % (elem.get('class', ''), elem.get('id', ''))
            #print(describe(elem), s)
            #if s == 'module__footer':
            #    print(REGEXES['unlikelyCandidatesRe'].search(s))
            if len(s) < 2:
                continue
            if REGEXES['unlikelyCandidatesRe'].search(s) and (not REGEXES['okMaybeItsACandidateRe'].search(s)) and elem.tag not in ['html', 'body']:
                #("Removing unlikely candidate - %s" % describe(elem))
                elements_to_drop.append(elem)
                # elem.drop_tree()
        for elem in elements_to_drop:
            #print(describe(elem))
            elem.drop_tree()
        #print(self.html.xpath("//div[@class='newstext']"))
        #print(self.html.xpath("//div[@class='swm_container']"))
        #print(self.html.xpath("//div[@class='layout__container']"))
        #print(etree.tostring(self.html, pretty_print=True))
        #print(len(elements_to_drop))
        #print(self.html.xpath("//div[@id='footer']"))
        #print(self.html.xpath('count(.//*)'))
        #print(ind)

    def transform_misused_divs_into_paragraphs(self):
        for elem in self.tags(self.html, 'div'):
            # transform <div>s that do not contain other block elements into
            # <p>s
            #FIXME: The current implementation ignores all descendants that
            # are not direct children of elem
            # This results in incorrect results in case there is an <img>
            # buried within an <a> for example
            if not REGEXES['divToPElementsRe'].search(
                    str_(b''.join(map(tostring, list(elem))))):
                #log.debug("Altering %s to p" % (describe(elem)))
                elem.tag = "p"
                #print "Fixed element "+describe(elem)
        for elem in self.tags(self.html, 'div'):
            if elem.text and elem.text.strip():
                p = fragment_fromstring('<p/>')
                p.text = elem.text
                elem.text = None
                elem.insert(0, p)
                #print "Appended "+tounicode(p)+" to "+describe(elem)

            for pos, child in reversed(list(enumerate(elem))):
                if child.tail and child.tail.strip():
                    p = fragment_fromstring('<p/>')
                    p.text = child.tail
                    child.tail = None
                    elem.insert(pos + 1, p)
                    #print("Inserted "+tounicode(p)+" to "+describe(elem)+"child: "+describe(child))
                if child.tag == 'br':
                    #print 'Dropped <br> at '+describe(elem)
                    child.drop_tree()
        #print(html.unescape(etree.tostring(self.html, pretty_print=True).decode("utf-8")))
        #exit()

    def tags(self, node, *tag_names):
        for tag_name in tag_names:
            for e in node.findall('.//%s' % tag_name):
                yield e


    def score_title_rate(self, elem):
        text = elem.text_content()
        text_lemmas = mystem.lemmatize(text)
        rate = 0
        for lemma in text_lemmas:
            if lemma in self.title_lemmas:
                rate += 1
        return rate / len(text_lemmas)


    def reverse_tags(self, node, *tag_names):
        for tag_name in tag_names:
            for e in reversed(node.findall('.//%s' % tag_name)):
                yield e

    def sanitize(self, node, candidates, fusion_clearing = True):
        MIN_LEN = self.min_text_length
        for header in self.tags(node, "h1", "h2", "h3", "h4", "h5", "h6"):
            if self.class_weight(header) < 0 or self.get_link_density(header) > 0.33:
                header.drop_tree()

        if fusion_clearing:
            #print("FUSION CLEANING")
            self.rf_sanitize(node)
            #print(html.unescape(etree.tostring(node, pretty_print=True).decode("utf-8")))
            #exit()

        for elem in self.tags(node, "form", "textarea"):
            elem.drop_tree()

        """
        for elem in self.tags(node, "iframe"):
            if "src" in elem.attrib and REGEXES["videoRe"].search(elem.attrib["src"]):
                elem.text = "VIDEO" # ADD content to iframe text node to force <iframe></iframe> proper output
            else:
                elem.drop_tree()
        """

        allowed = {}
        # Conditionally clean <table>s, <ul>s, and <div>s
        for el in self.reverse_tags(node, "table", "ul", "div"):
            if el in allowed:
                continue
            weight = self.class_weight(el)
            if el in candidates:
                content_score = candidates[el]['content_score']
                #print '!',el, '-> %6.3f' % content_score
            else:
                content_score = 0
            tag = el.tag

            if weight + content_score < 0:
                #log.debug("Removed %s with score %6.3f and weight %-3s" %(describe(el), content_score, weight, ))
                el.drop_tree()
            elif el.text_content().count(",") < 10:
                counts = {}
                for kind in ['p', 'img', 'li', 'a', 'embed', 'input']:
                    counts[kind] = len(el.findall('.//%s' % kind))
                counts["li"] -= 100
                counts["input"] -= len(el.findall('.//input[@type="hidden"]'))

                # Count the text length excluding any surrounding whitespace
                content_length = text_length(el)
                link_density = self.get_link_density(el)
                parent_node = el.getparent()
                if parent_node is not None:
                    if parent_node in candidates:
                        content_score = candidates[parent_node]['content_score']
                    else:
                        content_score = 0
                #if parent_node is not None:
                    #pweight = self.class_weight(parent_node) + content_score
                    #pname = describe(parent_node)
                #else:
                    #pweight = 0
                    #pname = "no parent"
                to_remove = False
                reason = ""

                #if el.tag == 'div' and counts["img"] >= 1:
                #    continue
                if counts["p"] and counts["img"] > 1+counts["p"]*1.3:
                    reason = "too many images (%s)" % counts["img"]
                    to_remove = True
                elif counts["li"] > counts["p"] and tag != "ul" and tag != "ol":
                    reason = "more <li>s than <p>s"
                    to_remove = True
                elif counts["input"] > (counts["p"] / 3):
                    reason = "less than 3x <p>s than <input>s"
                    to_remove = True
                elif content_length < MIN_LEN and counts["img"] == 0:
                    reason = "too short content length %s without a single image" % content_length
                    to_remove = True
                elif content_length < MIN_LEN and counts["img"] > 2:
                    reason = "too short content length %s and too many images" % content_length
                    to_remove = True
                elif weight < 25 and link_density > 0.2:
                        reason = "too many links %.3f for its weight %s" % (
                            link_density, weight)
                        to_remove = True
                elif weight >= 25 and link_density > 0.5:
                    reason = "too many links %.3f for its weight %s" % (
                        link_density, weight)
                    to_remove = True
                elif (counts["embed"] == 1 and content_length < 75) or counts["embed"] > 1:
                    reason = "<embed>s with too short content length, or too many <embed>s"
                    to_remove = True
                elif not content_length:
                    reason = "no content"
                    to_remove = True
#                if el.tag == 'div' and counts['img'] >= 1 and to_remove:
#                    imgs = el.findall('.//img')
#                    valid_img = False
#                    log.debug(tounicode(el))
#                    for img in imgs:
#
#                        height = img.get('height')
#                        text_length = img.get('text_length')
#                        log.debug ("height %s text_length %s" %(repr(height), repr(text_length)))
#                        if to_int(height) >= 100 or to_int(text_length) >= 100:
#                            valid_img = True
#                            log.debug("valid image" + tounicode(img))
#                            break
#                    if valid_img:
#                        to_remove = False
#                        log.debug("Allowing %s" %el.text_content())
#                        for desnode in self.tags(el, "table", "ul", "div"):
#                            allowed[desnode] = True

                    #find x non empty preceding and succeeding siblings
                    i, j = 0, 0
                    x = 1
                    siblings = []
                    for sib in el.itersiblings():
                        #log.debug(sib.text_content())
                        sib_content_length = text_length(sib)
                        if sib_content_length:
                            i =+ 1
                            siblings.append(sib_content_length)
                            if i == x:
                                break
                    for sib in el.itersiblings(preceding=True):
                        #log.debug(sib.text_content())
                        sib_content_length = text_length(sib)
                        if sib_content_length:
                            j =+ 1
                            siblings.append(sib_content_length)
                            if j == x:
                                break
                    #log.debug(str_(siblings))
                    if siblings and sum(siblings) > 1000:
                        to_remove = False
                        #log.debug("Allowing %s" % describe(el))
                        for desnode in self.tags(el, "table", "ul", "div"):
                            allowed[desnode] = True

                if to_remove:
                    #log.debug("Removed %6.3f %s with weight %s cause it has %s." %(content_score, describe(el), weight, reason))
                    #print tounicode(el)
                    #log.debug("pname %s pweight %.3f" %(pname, pweight))
                    el.drop_tree()
                else:
                    #log.debug("Not removing %s of length %s: %s" % (describe(el), content_length, text_content(el)))
                    pass

        self.html = node
        return self.get_clean_html()

    def rf_sanitize(self, elem):
        p_or_div = elem.tag in ['p', 'div']

        has_children = False
        has_p_or_div = False
        to_drop = False
        if to_plain_text(elem.text_content()) == self.title_text:
            to_drop = True
        else:
            children = elem.xpath("child::node()")
            if len(children):
                was_children = True
            else:
                was_children = False
            for child in children:
                if isinstance(child, HtmlElement):
                    has_p_or_div0, was_dropped = self.rf_sanitize(child)
                    has_p_or_div = has_p_or_div or has_p_or_div0
                    if not was_dropped:
                        has_children = True
                #elif str(child).strip():
                else:
                    has_children = True
            if not has_children and was_children:
                to_drop = True
            elif not has_p_or_div and p_or_div:
                txt = elem.text_content().strip()
                #print(txt)
                #print(re.match(REGEXES["rfBadStartWithLink"], txt))
                if (self.get_link_density(elem) > 0 and (
                            re.match(REGEXES["rfBadStartWithLink"], txt) or re.search(REGEXES["rfBadSearchWithLink"], txt))) \
                        or re.match(REGEXES["rfBadStart"], txt) or re.search(REGEXES["rfBadSearch"], txt):
                    print("fusion_clearing: ", txt)
                    to_drop = True
        if to_drop:
            #print(describe(elem))
            elem.drop_tree()
            p_or_div = False
            has_p_or_div = False
        #print(to_drop, p_or_div, has_p_or_div, has_children)
        return p_or_div or has_p_or_div, to_drop


if __name__ == '__main__':
    pass