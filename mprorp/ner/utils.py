from collections import defaultdict

import numpy as np
import mprorp.ner.data_utils.utils as du

class Vocab(object):

    def __init__(self):
        self.word_to_index = {}
        self.index_to_word = {}
        self.word_freq = defaultdict(int)
        self.total_words = 0
        self.unknown = '<unk>'
        self.add_word(self.unknown, count=0)

    def add_word(self, word, count=1):
        if word not in self.word_to_index:
              index = len(self.word_to_index)
              self.word_to_index[word] = index
              self.index_to_word[index] = word
        self.word_freq[word] += count

    def construct(self, words):
        for word in words:
            self.add_word(word)
        self.total_words = float(sum(self.word_freq.values()))
        print('{} total words with {} uniques'.format(self.total_words, len(self.word_freq)))

    def encode(self, word):
        if word not in self.word_to_index:
            word = self.unknown
        return self.word_to_index[word]

    def decode(self, index):
        return self.index_to_word[index]

    def __len__(self):
        return len(self.word_freq)


def calculate_perplexity(log_probs):
    # https://web.stanford.edu/class/cs124/lec/languagemodeling.pdf
    perp = 0
    for p in log_probs:
        perp += -p
    return np.exp(perp / len(log_probs))


def get_ptb_dataset(dataset='train'):
    fn = 'data/ptb/ptb.{}.txt'
    for line in open(fn.format(dataset)):
        for word in line.split():
            yield word
    # Add token to the end of the line
    # Equivalent to <eos> in:
    # https://github.com/wojzaremba/lstm/blob/master/data.lua#L32
    # https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/ptb/reader.py#L31
        yield '<eos>'


def ptb_iterator(raw_data, batch_size, num_steps):
    # Pulled from https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/ptb/reader.py#L82
    raw_data = np.array(raw_data, dtype=np.int32)
    data_len = len(raw_data)
    batch_len = data_len // batch_size
    data = np.zeros([batch_size, batch_len], dtype=np.int32)
    for i in range(batch_size):
        data[i] = raw_data[batch_len * i:batch_len * (i + 1)]
    epoch_size = (batch_len - 1) // num_steps
    if epoch_size == 0:
        raise ValueError("epoch_size == 0, decrease batch_size or num_steps")
    for i in range(epoch_size):
        x = data[:, i * num_steps:(i + 1) * num_steps]
        y = data[:, i * num_steps + 1:(i + 1) * num_steps + 1]
        yield (x, y)


def sample(a, temperature=1.0):
    # helper function to sample an index from a probability array
    # from https://github.com/fchollet/keras/blob/master/examples/lstm_text_generation.py
    a = np.log(a) / temperature
    a = np.exp(a) / np.sum(np.exp(a))
    return np.argmax(np.random.multinomial(1, a, 1))


def data_iterator(orig_X, orig_y=None, orig_features=None, batch_size=32, label_size=2, shuffle=False):
    # Optionally shuffle the data before training
    if shuffle:
        indices = np.random.permutation(len(orig_X))
        data_X = orig_X[indices]
        data_y = orig_y[indices] if np.any(orig_y) else None
        data_F = orig_features[indices] if np.any(orig_features) else None
    else:
        data_X = orig_X
        data_y = orig_y
        data_F = orig_features
    ###
    total_processed_examples = 0
    total_steps = int(np.ceil(len(data_X) / float(batch_size)))
    for step in range(total_steps):
        # Create the batch by selecting up to batch_size elements
        batch_start = step * batch_size
        x = data_X[batch_start:batch_start + batch_size]
        # Convert our target from the class index to a one hot vector
        y = None
        if np.any(data_y):
            y_indices = data_y[batch_start:batch_start + batch_size]
            y = np.zeros((len(x), label_size), dtype=np.int32)
            y[np.arange(len(y_indices)), y_indices] = 1
        f = None
        if np.any(data_F):
            f = data_F[batch_start:batch_start + batch_size]
        ###
        yield x, y, f
        total_processed_examples += len(x)
    # Sanity check to make sure we iterated over all the dataset as intended
    assert total_processed_examples == len(data_X), 'Expected {} and processed {}'.format(len(data_X), total_processed_examples)


def convert_y(y_indices, label_size):
    res = np.zeros((len(y_indices), label_size), dtype=np.int32)
    res[np.arange(len(y_indices)), y_indices] = 1
    return res


def data_iterator2(train_data, word_to_num, tag_to_num, config_features, features_size,  features_length, window_size, batch_size=32, label_size=2, shuffle=False):
    # Optionally shuffle the data before training
    pad = int((window_size - 1) / 2)
    to_add = batch_size
    docs = {}
    last_word = 0
    sentence_end = True
    for doc_id in train_data['words']:
        words = train_data['words'][doc_id]
        # Будем добавляьть куски текущего документа, пока не окажется, что осташегося куска недостаточно
        while last_word + pad + 1 + to_add < len(words):
            # к слову с номером last_word + pad + 1 + to_add  можно обратиться
            docs[doc_id] = {'ind_begin': last_word, 'start_with_zero': sentence_end} # Это всегда так
            # compare sent_index of words
            if words[last_word + to_add - pad][0] == words[last_word + pad + 1 + to_add][0]:
                # предложение здесь не прерывается, возьмем этот кусок и вернем окна
                docs[doc_id]['ind_end'] = last_word + to_add + pad
                docs[doc_id]['end_with_zero'] = False
                feat_train, X_train, y_train, _, _ = du.docs_to_windows2(train_data, word_to_num,
                                                                         tag_to_num, config_features,
                                                                         features_size, features_length,
                                                                         wsize=window_size, docs=docs)
                yield X_train, convert_y(y_train, label_size), feat_train
                # Нужно подготовить начало следующего куска
                docs = {}
                last_word = last_word - pad + to_add # Т.е. предложение не закончилось берем pad слов для образования окна
                sentence_end = False
                to_add = batch_size
            else:
                # Предложение рвется на этом участке. Найдем слово, на котором происходит разрыв
                last_word = last_word + to_add - pad + 1
                while words[last_word][0] == words[last_word - 1][0]:
                    last_word += 1
                docs[doc_id]['ind_end'] = last_word
                feat_train, X_train, y_train, _, _ = du.docs_to_windows2(train_data, word_to_num,
                                                                         tag_to_num, config_features,
                                                                         features_size, features_length,
                                                                         wsize=window_size, docs=docs)
                yield X_train, convert_y(y_train, label_size), feat_train
                # Нужно подготовить начало следующего куска
                docs = {}
                sentence_end = True
                to_add = batch_size
        # Документа не хватает, чтобы сформировать batch
        docs[doc_id] = {'ind_begin': last_word, 'start_with_zero': sentence_end}  # Это всегда так
        if last_word + to_add - pad < len(words):
            # Не хватает меньше окна, поэтому возьмем, что есть, а следующую итерацию начнем со следующего документа
            feat_train, X_train, y_train, _, _ = du.docs_to_windows2(train_data, word_to_num,
                                                                     tag_to_num, config_features,
                                                                     features_size, features_length,
                                                                     wsize=window_size, docs=docs)
            yield X_train, convert_y(y_train, label_size), feat_train
            # Нужно подготовить начало следующего куска
            docs = {}
            to_add = batch_size
        else:
            # Возьмем часть этого документа и часть следующего
            # Для этого просто учтем (вычтем) сколько слов из этого документа будут использованы
            to_add -= len(words) - last_word
            if not sentence_end:
                # Если кусок начинается не сначала предложения, неколько слов уйдут аа первое окно
                to_add += pad

        last_word = 0
        sentence_end = True

