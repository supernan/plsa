#coding=utf-8

import numpy as np
import words_cluster as wc

cutlist = "。！？".decode("utf-8")
#key_words = ["货物","危险","装箱","业务","安置","逆行","中转","世界","最帅","年"]
#key_words = ["顿","近震","ML","震级","地震","记录","公安局","分","台网","火光冲天"]
key_words = ["北京","医疗","空气质量","今日","血液","指数","包括","污染物","重症","中午"]

corpus_path = "/home/zhounan/corpus/events/sample4" #要扫描的语料路径
topic_words_path = "/home/zhounan/project/ict/plsa/plsa/data/sample4/topic_words" #主题模型生产的话题词
min_keys = 2 #句子中包含的最小关键词个数, 大于此值才统计关键词的共现情况
tf_thresh = 5 #话题词共现的阈值
min_len = 3 #话题词的最小长度





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



def generate_cluster(path, topic_words):
    """
    生成文本话题簇
    """
    f = open(path)
    text_clusters = dict()
    snips_clusters = dict()
    for line in f:
        for topic_id in topic_words:
            snips_clusters[topic_id] = ""
            words = topic_words[topic_id]
            if wc.key_words_match(line.strip(), words):
                if text_clusters.has_key(topic_id):
                    text_clusters[topic_id].append(line.strip())
                else:
                    text_clusters[topic_id] = []
                    text_clusters[topic_id].append(line.strip())
    return text_clusters

            
if __name__ == '__main__':
    topic_words = wc.topic_words_discocery(topic_words_path, corpus_path, tf_thresh, min_len)
    text_clusters = generate_cluster(corpus_path, topic_words)
    for tid in topic_words:
        print ','.join(topic_words[tid])
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

