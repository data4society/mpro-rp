import string
from gensim.models.wrappers.fasttext import FastText
import numpy as np
import pickle as pickle
import math
import tensorflow as tf
from mprorp.config.settings import learning_parameters as lp

if 'fasttext' in lp:
    fasttext_params = lp['fasttext']
    MODELS_PATH = "/home/mprorp/models/"
    embedding_model = FastText.load_fasttext_format(MODELS_PATH+fasttext_params['embedding_model'])
    TF_STEPS = fasttext_params['tf_steps']
    REG_COEF = fasttext_params['reg_coef']
    LR = fasttext_params['lr']
    print("MODEL READY!")


def compute_embedding(txt):
    """compute fasttext embedding for one text"""
    vect = bag(embedding_model, txt)
    return vect


def reg_fasttext_embedding(doc):
    """compute embedding in regular process"""
    emb = compute_embedding(doc.stripped)
    doc.fasttext_embedding = emb.tolist()


def learning(embs, ans, filename):
    """compute fasttext model by document's embeddings and answers"""
    batch_size = len(ans)#min(len(ans), 100)
    #answers_array = np.zeros((batch_size, 1))
    answers_array = np.zeros((len(ans), 1))
    answers_array[:, 0] = ans
    model = build_rubric_model(embs, answers_array, batch_size)
    with open(MODELS_PATH+filename, 'wb') as f:
        pickle.dump(model, f)
    return model


def get_embedding_vector(txt):
    """get special embedding vector"""
    return np.concatenate([compute_embedding(txt),np.array([1])])


def get_answer_by_model_name(filename, emb_vec):
    """get probability answer for embedding by model name"""
    with open(MODELS_PATH+filename, 'rb') as f:
        model = pickle.load(f)
    return sigmoid(np.dot(emb_vec, model))


def get_answer(model, txt):
    """get probability answer for doc by model"""
    emb_vec = get_embedding_vector(txt)
    probability = sigmoid(np.dot(emb_vec, model))
    return probability


# translation table usable for str.translate() - removing punctuation and digits
TABLE = str.maketrans({key: None for key in string.punctuation+string.digits})

def parse(model,line):
    line = line.lower()
    line = line.translate(TABLE)
    words = line.split()
    known = []
    for word in words:
        try:
            model[word] # проверка, знает ли модель n-граммы
            known.append(word)
        except:
            #print('{} is unknown'.format(word))
            continue
    #print('length of words is {}. Length of known words is {}'.format(len(words), len(known)))
    return(known)


#складываем покомпонентно и делим на количество векторов-слов
def bag(model, line):
    words = parse(model, line)
    #bag_embed = np.array
    embed = model[words]
    bag_embed = sum(model[words])/len(words)
    return bag_embed


def build_rubric_model(tr_data, labels, batch_size):

    vec_size = len(tr_data[0])
    graph = tf.Graph()

    with graph.as_default(), tf.device('/cpu:0'):
        # Input data.
        train_dataset = tf.placeholder(tf.float32, shape=[batch_size, vec_size])
        train_labels = tf.placeholder(tf.float32, shape=[batch_size, 1])

        # Variables.
        weights = tf.Variable(tf.random_uniform([vec_size, 1], -1.0, 1.0))
        # tf.add_to_collection('total_loss', 0.5 * reg_softmax * tf.nn.l2_loss(weights))
        bias = tf.Variable(0.00001)

        y = tf.matmul(train_dataset, weights) + bias

        cross_entropy_array = tf.log(tf.sigmoid(y)) * train_labels + tf.log(1 - tf.sigmoid(y)) * (1 - train_labels)

        cross_entropy = - tf.reduce_mean(cross_entropy_array) + tf.reduce_mean(weights * weights) * REG_COEF

        global_step = tf.Variable(0, trainable=False)
        learning_rate = tf.train.exponential_decay(LR, global_step,
												   1000, 0.96, staircase=True)
        # Passing global_step to minimize() will increment it at each step.
        train_step = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(cross_entropy, global_step = global_step)
        init = tf.initialize_all_variables()

        sess = tf.Session()
        sess.run(init)

        j = 0
        for i in range(TF_STEPS):
            sess.run(train_step, feed_dict={train_dataset: tr_data[j:j+batch_size], train_labels: labels[j:j+batch_size]})
            j = j + batch_size
            if j + batch_size > len(tr_data):
                j = (j + batch_size) % len(tr_data)
                # хвостик tr_data не будет участвовать в обучении
                # ничего страшного. За счет сдвига начального номера j этот хвостик будет все время разным, так что почти все
                # документы поучаствуют


    model = weights.eval(sess)[:, 0]
    model = model.tolist()
    model.append(float(bias.eval(sess)))
    return model


def sigmoid(x):
    """sigmoid for value x"""
    return 1/(1 + math.exp(-x))
