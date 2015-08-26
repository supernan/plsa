
#coding=utf-8
"""
模块功能:
同类事件不同子话题共性抽取
"""
import numpy as np
import math
import words_cluster as wc
import esm
import extract as ex

tf_thresh = 10
min_len = 3 #common words的最小长度
rate = 0.8 #子话题关键词匹配的准确率阈值
cutlist = "。！？".decode("utf-8")


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
    return score_mat


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

"""
def generate_summary(key_words, corpus_path):
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
"""

def load_df_map(path):
    """
    加载全局df表
    """
    f = open(path)
    df_map = dict()
    for line in f:
        parts = line.strip().split(" ")
        df_map[parts[0]] = float(parts[1])
    return df_map


def load_word_label_map(path):
    """
    加载标注好的背景词
    """
    f = open(path)
    word_label_map = dict()
    for line in f:
        labels = []
        parts = line.split("||")
        word = parts[0]
        parts = parts[1:]
        for part in parts:
            labels.append(part.strip())
        word_label_map[word] = labels
    return word_label_map
        


def get_background_index(back_path):
    """
    获得由类别主题模型得到背景词
    """
    f = open(back_path)
    index = esm.Index()
    for line in f:
        parts = line.split(" ")
        for part in parts:
            pairs = part.split(":")
            index.enter(pairs[0])

        #index.enter(line.strip().split(" ")[0])
    index.fix()
    return index


def get_common_background(cluster_A, cluster_B, back_index, df_map, min_len):
    """
    得到两个子话题共同的背景词
    """
    common_words = dict()
    cluster_A_map = dict()
    cluster_B_map = dict()
    
    for text in cluster_A:
        rets = back_index.query(text)
        for word in rets:
            if cluster_A_map.has_key(word[1]):
                cluster_A_map[word[1]] += 1
            else:
                cluster_A_map[word[1]] = 1
    
    for text in cluster_B:
        rets = back_index.query(text)
        for word in rets:
            if word[1] in cluster_A_map:
                if cluster_B_map.has_key(word[1]):
                    cluster_B_map[word[1]] += 1
                else:
                    cluster_B_map[word[1]] = 1
    
    for key in cluster_A_map:
        A_count = cluster_A_map[key]
        if not cluster_B_map.has_key(key):
            continue
        B_count = cluster_B_map[key]
        if abs(A_count - B_count) < min(A_count, B_count) / 2:
            common_words[key] = A_count + B_count
    
    for key in common_words:
        if df_map.has_key(key):
            common_words[key] = math.log(float(common_words[key])) * math.log(float(1) / float(df_map[key])) #/ float(df_map[key])
    if len(common_words) < min_len:
        return []
    ret = []
    words =  sorted(common_words.items(), key=lambda d: d[1], reverse = True)[:4]
    for i in range(len(words)):
        ret.append(words[i][0])
    return ret


def choose_best_label(word_label_map, common_words):
    """
    选择共同背景词的最佳标签
    """
    label_count_map = dict()
    for word in common_words:
        labels = word_label_map[word]
        for label in labels:
            if label_count_map.has_key(label):
                label_count_map[label] += 1
            else:
                label_count_map[label] = 1
    last_count = 0
    all_same = True
    for label in label_count_map:
        if last_count != 0 and label_count_map[label] != last_count:
            all_same = False
            break
        else:
            last_count = label_count_map[label]
    if all_same:
        return "NONE"
    max_count = 0
    best_label = ""
    for label in label_count_map:
        if label_count_map[label] > max_count:
            max_count = label_count_map[label]
            best_label = label
    return best_label


def event_in_common(word_label_map, back_index, corpus_path, event_A, event_B, df_map, A_name, B_name, min_len, rate):
    """
    比较两个事件任意子话题对的共同点
    """
    size_A = len(event_A)
    size_B = len(event_B)
    cluster_A, max_time_A, min_time_A = ex.generate_cluster_time(corpus_path, event_A, rate)
    cluster_B, max_time_B, min_time_B = ex.generate_cluster_time(corpus_path, event_B, rate)
    for i in range(size_A):
        for j in range(size_B):
            common_words = get_common_background(cluster_A[i], cluster_B[j], back_index, df_map, min_len)
            if len(common_words) == 0:
                continue
            best_label = choose_best_label(word_label_map, common_words)
            if best_label == "NONE":
                continue
            print 
            print "================================================="
            print "common words: " + ','.join(common_words) + " " + "[" + best_label + "]"
            print "sub_topic " + A_name + " " + str(i) + " " + ','.join(event_A[i]) + " " + min_time_A[i] + " " + max_time_A[i]
            print "sub_topic " + B_name + " " + str(j) + " " + ','.join(event_B[j]) + " " + min_time_B[j] + " " + max_time_B[j]
            print "=================================================="
            print


def events_analysis(filenames, total_corpus_path, df_path, back_path, label_path, min_len, rate):
    key_set = set()
    back_index = get_background_index(back_path)
    word_label_map = load_word_label_map(label_path)
    df_map = load_df_map(df_path)
    for i in range(len(filenames)):
        for j in range(len(filenames)):
            if i == j:
                continue
            key = ""
            if i > j:
                key = str(i) + "&" + str(j)
            else:
                key = str(j) + "&" + str(i)
            if key in key_set:
                continue
            else:
                key_set.add(key)
                print filenames[i], filenames[j]
                event_A, event_B = load_event(filenames[i], filenames[j])
                event_in_common(word_label_map, back_index, total_corpus_path, event_A, event_B, df_map, filenames[i], filenames[j], min_len, rate)
                print "End"
                print
                
            




if __name__ == '__main__':
    filenames = ["./niboer", "./sichuan", "./taiwan", "./xinjiang"]
    events_analysis(filenames, "/home/zhounan/corpus/mongo_data/news_event/earthquake/earthquake_time", "./earthquake_df", "../data/earthquake/topic_words",
                    "../data/earthquake/topic_words_label", min_len, rate)
    #event_A, event_B = load_event("./canhong", "./sudiluo")
    #df_map = load_df_map("./taifeng_back")
    #w2v= load_word2vec("/home/zhounan/local/word2vec/output/tianfeng.vec")
    #score_mat = event_compare(event_A, event_B, w2v)
    #event_in_common("../data/taifeng/topic_words", "/home/zhounan/corpus/events/taifeng_event", event_A, event_B, df_map)
    """
    print ','.join(topic_A)
    print ','.join(topic_B)
    print
    key_words = topic_A + topic_B
    rets = generate_summary(key_words, "/home/zhounan/corpus/mongo_data/weibo_event_2")
    for k in rets:
        print ','.join(rets[k])
    """



