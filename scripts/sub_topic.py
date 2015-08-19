#coding=utf-8
"""
模块功能:
同类事件不同子话题共性抽取
"""
import numpy as np
import words_cluster as wc
import esm
import extract as ex

tf_thresh = 10
min_len = 4


def load_word2vec(path):
    """
    加载词向量
    """
    is_first_line = True
    f = open(path)
    w2v = dict()
    for line in f:
        if is_first_line:
            is_first_line = False
            continue
        else:
            parts = line.strip().split(" ")
            word = parts[0]
            parts = parts[1:]
            vec = []
            for part in parts:
                vec.append(float(part))
            w2v[word] = np.array(vec)
    return w2v


def load_event(A_path, B_path):
    """
    加载事件的所有主题词
    """
    f_a = open(A_path)
    f_b = open(B_path)
    event_A = []
    event_B = []
    for line in f_a:
        words = line.strip().split(',')
        event_A.append(words)
    for line in f_b:
        words = line.strip().split(',')
        event_B.append(words)
    return event_A, event_B



def find_best_match(scores):
    """
    查找最佳匹配的子话题
    """
    n, m = np.shape(scores)
    max_x = 0
    max_y = 0
    max_val = 0.0
    for i in range(n):
        for j in range(m):
            if scores[i, j] > max_val:
                max_x = i
                max_y = j
                max_val = scores[i, j]
    return max_x, max_y


def event_compare(event_A, event_B, w2v):
    """
    返回两个事件最匹配的子话题
    """
    size_A = len(event_A)
    size_B = len(event_B)
    score_mat = np.mat(np.zeros((size_A, size_B)))
    for i in range(size_A):
        for j in range(size_B):
            topic_A = event_A[i]
            topic_B = event_B[j]
            score_mat[i, j] = topic_compare(topic_A, topic_B, w2v)
    index_A, index_B = find_best_match(score_mat)
    return event_A[index_A], event_B[index_B]


def topic_compare(topic_A, topic_B, w2v):
    """
    计算子话题相似度得分
    """
    size_A = len(topic_A)
    size_B = len(topic_B)
    score_mat = np.mat(np.zeros((size_A, size_B)))
    for i in range(size_A):
        for j in range(size_B):
            if w2v.has_key(topic_A[i]):
                v_a = w2v[topic_A[i]]
            else:
                v_a = []
            if w2v.has_key(topic_B[j]):
                v_b = w2v[topic_B[j]]
            else:
                v_b = []
            score_mat[i, j] = word_similarity(v_a, v_b)
            #print topic_A[i], topic_B[j], score_mat[i, j]
    score = score_mat.sum()
    return score



def word_similarity(v1, v2):
    """
    计算词向量相似度
    """
    if len(v1) == 0:
        vec1 = np.mat(np.zeros(200))
    else:
        vec1 = np.mat(v1)
    if len(v2) == 0:
        vec2 = np.mat(np.zeros(200))
    else:
        vec2 = np.mat(v2)
    num = float(vec1 * vec2.T)
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if denom == 0:
        cos = -1
    else:
        cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim


def generate_summary(key_words, corpus_path):
    """
    生成相似子话题的共同摘要
    """
    size = len(key_words)
    M = np.mat(np.zeros((size, size)))
    f = open(corpus_path)
    for line in f:
        wc.make_common_matrix(line, M, key_words)
    topic_words = []
    C = wc.key_words_analysis(M, tf_thresh, key_words)
    for key in C:
        if len(C[key]) >= min_len:
            topic_words.append(C[key])
    ret_topics = dict()
    for i in range(len(topic_words)):
        ret_topics[i] = topic_words[i]
    return ret_topics
    

def get_background_index(back_path):
    f = open(back_path)
    index = esm.Index()
    for line in f:
        """
        parts = line.split(" ")
        for part in parts:
            pairs = part.split(":")
            index.enter(pairs[0])
        """
        index.enter(line.strip().split(" ")[0])
    index.fix()
    return index
    

def get_common_background(cluster_A, cluster_B, back_index):
    backgroud_set = set()
    common_words = set()
    for text in cluster_A:
        rets = back_index.query(text)
        for word in rets:
            backgroud_set.add(word[1])
    for text in cluster_B:
        rets = back_index.query(text)
        for word in rets:
            if word[1] in backgroud_set:
                common_words.add(word[1])
    return common_words


def event_in_common(back_path, corpus_path, event_A, event_B):
    back_index = get_background_index(back_path)
    size_A = len(event_A)
    size_B = len(event_B)
    cluster_A = ex.generate_cluster(corpus_path, event_A)
    cluster_B = ex.generate_cluster(corpus_path, event_B)
    for i in range(size_A):
        for j in range(size_B):
            common_words = get_common_background(cluster_A[i], cluster_B[j], back_index)
            print 
            print "================================================="
            print "common words: " + ','.join(common_words)
            print "sub_topic A: " + ','.join(event_A[i])
            print "sub_topic B: " + ','.join(event_B[j])
            print "=================================================="
            print




if __name__ == '__main__':
    event_A, event_B = load_event("./niboer", "./others")
    w2v = load_word2vec("/home/zhounan/local/word2vec/output/weibo_event_2.vec")
    event_in_common("./back_words", "/home/zhounan/corpus/mongo_data/weibo_event_2", event_A, event_B)
    """
    topic_A, topic_B = event_compare(event_A, event_B, w2v)
    print ','.join(topic_A)
    print ','.join(topic_B)
    print
    key_words = topic_A + topic_B
    rets = generate_summary(key_words, "/home/zhounan/corpus/mongo_data/weibo_event_2")
    for k in rets:
        print ','.join(rets[k])
    """



