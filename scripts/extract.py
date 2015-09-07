#coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
import words_cluster as wc
import datetime
import time
from matplotlib.font_manager import FontProperties
from matplotlib.pyplot import plot,savefig  

cutlist = "。！？".decode("utf-8")

corpus_path = "/home/zhounan/corpus/mongo_data/news_event/zibo_explosion_hour" #要扫描的语料路径
topic_words_path = "/home/zhounan/project/ict/plsa/plsa/data/zibo_explosion/topic_words" #主题模型生产的话题词
label_path="../data/zibo_explosion/labels"
filename = "zibo_explosion"
min_keys = 2 #句子中包含的最小关键词个数, 大于此值才统计关键词的共现情况
tf_thresh = 5 #话题词共现的阈值
min_len = 3 #话题词的最小长度



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
        if not word_label_map.has_key(word):
            word_label_map[word] = labels
        else:
            word_label_map[word] += labels
    return word_label_map


def generate_snips(line, words):
    sents = cut_sent(list(cutlist), list(line.strip().decode("utf-8")))
    max_count = 0
    best_sent = ""
    for sent in sents:
        count = 0
        for word in words:
            if sent.find(word.decode("utf-8")) != -1:
                count += 1
        if count >= max_count:
            max_count = count
            best_sent = sent.encode("utf-8")
    return max_count, best_sent


def extract_time(line):
	parts = line.strip().split("||")
	time_str = parts[0]
	return time_str


def generate_cluster_time(path, topic_words, rate):
    """
    生成文本话题簇
    """
    f = open(path)
    text_clusters = dict()
    max_time_dict = dict()
    min_time_dict = dict()
    topic_count_map = dict()
    for i in range(len(topic_words)):
        text_clusters[i] = []
    for i in range(len(topic_words)):
        topic_count_map[i] = dict()
    
    for line in f:
        for topic_id in range(len(topic_words)):
            words = topic_words[topic_id]
            if wc.key_words_match(line.strip(), words, rate):
		time = extract_time(line)
                if topic_count_map[topic_id].has_key(time):
                    topic_count_map[topic_id][time] += 1
                else:
                    topic_count_map[topic_id][time] = 1
                if text_clusters.has_key(topic_id):
                    text_clusters[topic_id].append(line.strip())
                else:
                    text_clusters[topic_id] = []
                    text_clusters[topic_id].append(line.strip())
    
    for tid in topic_count_map:
        time_count_map = topic_count_map[tid]
        time_list = sorted(time_count_map.items(), key=lambda d: d[0])
        if len(time_list) == 0:
            continue
        min_time = time_list[0][0]
        max_time = time_list[len(time_list) - 1][0]
        max_time_dict[tid] = max_time
        min_time_dict[tid] = min_time

    return text_clusters, topic_count_map, max_time_dict,  min_time_dict



def choose_sub_topic_best_label(topic_words, word_label_map, label_thresh):
    """
    选择子话题label
    """
    label_count_map = dict()
    best_label = "NONE"
    for word in topic_words:
        if not word_label_map.has_key(word):
            continue
        labels = word_label_map[word]
        for label in labels:
            if label_count_map.has_key(label):
                label_count_map[label] += 1
            else:
                label_count_map[label] = 1
    max_count = 0
    total_count = 0
    for label in label_count_map:
        total_count += label_count_map[label]
        if label_count_map[label] > max_count:
            max_count = label_count_map[label]
            best_label = label
    if max_count < total_count / label_thresh:
        best_label = "NONE"
    return best_label.strip()
    


def generate_cluster(path, topic_words):
    """
    生成文本话题簇
    """
    f = open(path)
    text_clusters = dict()
    for i in range(len(topic_words)):
        text_clusters[i] = []
    for line in f:
        for topic_id in range(len(topic_words)):
            words = topic_words[topic_id]
            if wc.key_words_match(line.strip(), words):
                if text_clusters.has_key(topic_id):
                    text_clusters[topic_id].append(line.strip())
                else:
                    text_clusters[topic_id] = []
                    text_clusters[topic_id].append(line.strip())
    return text_clusters
            


def set_step(x, y, step, size):
    """
    根据step调整数据
    """
    step *= 3600
    num = int(size / step) + 1
    ret_x = []
    for i in range(num):
        ret_x.append(i)
    ret_y = [0 for i in range(num)]
    for i in range(len(x)):
        pos = int((x[i] - x[0]) / step)
        ret_y[pos] += y[i]
    return ret_x, ret_y


def str2datetime(day, time_format='%Y-%m-%d %H'):
    """
    字符串转化成datetime对象
    """
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(day, time_format)))


def draw_graph(topic_count_map, topic_label_map, gap, filename):
    """
    绘制子话题热度折线图
    """
    font = FontProperties(fname=r"/home/zhounan/fonts/yahei.ttf", size=10)
    count = 1
    size = len(topic_count_map)
    for tid in topic_count_map:
        if len(topic_count_map[tid]) == 0:
            continue
        if topic_label_map[tid] == "NONE":
            continue
        time_count_map = topic_count_map[tid]
        if len(time_count_map) == 0:
            continue
        axis = plt.subplot(size/2, 2, count)
        count += 1
        time_list = sorted(time_count_map.items(), key=lambda d: d[0])
        y = []
        x = []
        for i in range(len(time_list)):
            date_obj = str2datetime(time_list[i][0])
            utc = time.mktime(date_obj.timetuple()) 
            x.append(utc)
            y.append(time_list[i][1])
        max_size = x[len(x) - 1] - x[0]
        ret_x, ret_y = set_step(x, y, gap, max_size)
        plt.plot(ret_x, ret_y)
        plt.title(topic_label_map[tid].decode("utf-8"), fontproperties=font)
        plt.sca(axis)
    plt.subplots_adjust(left=0.08, right=0.95, wspace=0.25, hspace=0.6)
    savefig("../data/pics/" + filename + "_" + str(gap) + ".jpg")
    plt.close() 


def generate_flow_chart(topic_label_map, min_time_dict):
    label_time_map = dict()
    time_label_map = dict()
    for tid in topic_label_map:
        if topic_label_map[tid] == "NONE":
            continue
        if not min_time_dict.has_key(tid):
            continue
        label = topic_label_map[tid]
        if label_time_map.has_key(label):
            label_time_map[label].append(min_time_dict[tid])
        else:
            label_time_map[label] = []
            label_time_map[label].append(min_time_dict[tid])
    for label in label_time_map:
        time_list = label_time_map[label]
        sorted_time_list = sorted(time_list)
        time = sorted_time_list[0]
        if time_label_map.has_key(time):
            time_label_map[time].append(label)
        else:
            time_label_map[time] = []
            time_label_map[time].append(label)
    sorted_time = sorted(time_label_map.items(), key=lambda d: d[0])
    for time_tuple in sorted_time:
        key = time_tuple[0]
        labels = time_tuple[1]
        print key, ','.join(labels)
        
        



if __name__ == '__main__':
    topic_words = wc.topic_words_discocery(topic_words_path, corpus_path, tf_thresh, min_len)
    word_label_map = load_word_label_map(label_path)
    text_clusters, topic_count_map, max_time_dict, min_time_dict = generate_cluster_time(corpus_path, topic_words, 1)
    topic_label_map = dict()
    for tid in topic_words:
        label = choose_sub_topic_best_label(topic_words[tid], word_label_map, 2)
        topic_label_map[tid] = label
        if label == "NONE" or len(text_clusters[tid]) == 0:
            continue
        print ','.join(topic_words[tid]), min_time_dict[tid], max_time_dict[tid], '[', label.strip(), ']'
    print
    generate_flow_chart(topic_label_map, min_time_dict)
    #draw_graph(topic_count_map, topic_label_map, 1, filename)
    #draw_graph(topic_count_map, topic_label_map, 2, filename)
    #draw_graph(topic_count_map, topic_label_map, 5, filename)
    """
    for cid in text_clusters:
        f = open("./cluster/sample/" + str(cid), 'w')
        words = topic_words[cid]
        words_str = ','.join(words)
        print words_str
        f.write(str(cid))
        f.write(": ")
        f.write(words_str)
        f.write('\n')
        for line in text_clusters[cid]:
            f.write(line)
            f.write('\n')
        f.close()
    """

