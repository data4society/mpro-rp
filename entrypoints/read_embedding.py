import sys
sys.path.insert(0, '..')
from mprorp.utils import home_dir
from gensim.models import word2vec


pre_embedding_from_file = home_dir + '/embeddings/news_win20.model.bin'
model_w2v = word2vec.Word2Vec.load_word2vec_format(pre_embedding_from_file, binary=True)
print(model_w2v['жизнь_S'])