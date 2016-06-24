"""shingling (estimate of compare two docs) from http://www.codeisart.ru/blog/python-shingles-algorithm/"""
def canonize(source):
        stop_symbols = '.,!?:;-\n\r()'

        stop_words = (u'это', u'как', u'так',
        u'и', u'в', u'над',
        u'к', u'до', u'не',
        u'на', u'но', u'за',
        u'то', u'с', u'ли',
        u'а', u'во', u'от',
        u'со', u'для', u'о',
        u'же', u'ну', u'вы',
        u'бы', u'что', u'кто',
        u'он', u'она')

        return ( [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)] )

def genshingle(source):
    import binascii
    shingleLen = 10 #длина шингла
    out = []
    for i in range(len(source)-(shingleLen-1)):
        out.append (binascii.crc32(' '.join( [x for x in source[i:i+shingleLen]] ).encode('utf-8')))

    return out

def compaire (source1,source2):
    same = 0
    for i in range(len(source1)):
        if source1[i] in source2:
            same = same + 1

    return same*2/float(len(source1) + len(source2))*100

def get_compare_estimate(text1, text2):

    cmp1 = genshingle(canonize(text1))
    cmp2 = genshingle(canonize(text2))

    return compaire(cmp1,cmp2)
