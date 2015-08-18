#coding=utf-8

import numpy as np


cutlist = "。！？".decode("utf-8")
min_keys = 2 #句子中包含的最小关键词个数, 大于此值才统计关键词的共现情况

def find_parent(pos, parents):
	"""
	并查集查找父亲节点
	"""
	if pos != parents[pos]:
		parents[pos] = find_parent(parents[pos], parents)
	return parents[pos]


def union(x, y, parents):
	"""
	并查集联合节点
	"""
	x_parent = find_parent(x, parents)
	y_parent = find_parent(y, parents)
	if x_parent == y_parent:
		return
	if x > y:
		parents[y] = x
	else:
		parents[x] = y


def find_token(cutlist, char):
	"""
	查找断句的标点
	"""
	if char in cutlist:
		return True
	else:
		return False


def cut_sent(cutlist, lines):
	"""
	句子切分
	"""
	sents = []
	line = []
	for char in lines:
		if find_token(cutlist, char):
			line.append(char)
			sents.append(''.join(line))
			line = []
		else:
			line.append(char)
	return sents


def make_common_matrix(line, m, key_words):
	"""
	构造关键词共现矩阵
	"""
	sents = cut_sent(list(cutlist), list(line.strip().decode("utf-8")))
	for sent in sents:
		words = []
		count = 0
		for i in range(len(key_words)):
			#print key_words[i], sent.encode("utf-8")
			if sent.find(key_words[i].decode("utf-8")) != -1:
				count += 1
				words.append(i)
		if count >= min_keys:
			for x in words:
				for y in words:
					if x != y:
						m[x, y] += 1
			#print sent.encode("utf-8"), "count: ", count, ",".join(words)


def key_words_analysis(M, thresh, key_words):
	"""
	分析关键词的关联,根据词的关联程度将词聚类
	"""
	parents = dict()
	m, n = np.shape(M)
	for i in range(m):
		parents[i] = i
	for x in range(m):
		for y in range(n):
			if M[x, y] >= thresh:
				union(x, y, parents)
	
	clusters = dict()
	for i in range(len(parents)):
		key = parents[i]
		if clusters.has_key(key):
			clusters[key].append(key_words[i])
		else:
			data = []
			data.append(key_words[i])
			clusters[key] = data
	return clusters
	

def key_words_match(text, key_words):
	"""
	判断文本是否完全与某一组关键词匹配
	"""
	flg = True
	for word in key_words:
		if text.find(word) == -1:
			flg = False
			break
	return flg

	
def read_topic_words(path):
	f = open(path)
	all_key_words = []
	for line in f:
		key_words = []
		words_pairs = line.strip().split(" ")
		for words_pair in words_pairs:
			parts = words_pair.split(":")
			key_words.append(parts[0])
		all_key_words.append(key_words)
	return all_key_words


def topic_words_discocery(topic_words_path, corpus_path, tf_thresh, min_len):
    """
    话题关键词发现
    """
    f = open(corpus_path)
    text_list = []
    for line in f:
	    text_list.append(line.strip())

    all_key_words = read_topic_words(topic_words_path)
    topic_words = []

    for key_words in all_key_words:
	    N = len(key_words)
	    m = np.mat(np.zeros((N, N)))
	    for line in text_list:
		make_common_matrix(line, m, key_words)
	    C = key_words_analysis(m, tf_thresh, key_words)
	    for key in C:
		    if len(C[key]) >= min_len:
			    topic_words.append(C[key])
    ret_topics = dict()
    for i in range(len(topic_words)):
        ret_topics[i] = topic_words[i]
    return ret_topics
