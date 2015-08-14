#coding=utf-8

import numpy as np


cutlist = "。！？".decode("utf-8")
#key_words = ["货物","危险","装箱","业务","安置","逆行","中转","世界","最帅","年"]
#key_words = ["顿","近震","ML","震级","地震","记录","公安局","分","台网","火光冲天"]
key_words = ["北京","医疗","空气质量","今日","血液","指数","包括","污染物","重症","中午"]


def find_parent(pos, parents):
	if pos != parents[pos]:
		parents[pos] = find_parent(parents[pos], parents)
	return parents[pos]


def union(x, y, parents):
	x_parent = find_parent(x, parents)
	y_parent = find_parent(y, parents)
	if x_parent == y_parent:
		return
	if x > y:
		parents[y] = x
	else:
		parents[x] = y


def find_token(cutlist, char):
	if char in cutlist:
		return True
	else:
		return False


def cut_sent(cutlist, lines):
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


def key_words_match(line, m, key_words):
	sents = cut_sent(list(cutlist), list(line.strip().decode("utf-8")))
	for sent in sents:
		words = []
		count = 0
		for i in range(len(key_words)):
			if sent.find(key_words[i].decode("utf-8")) != -1:
				count += 1
				words.append(i)
		if count >= 2:
			for x in words:
				for y in words:
					if x != y:
						m[x, y] += 1
			#print sent.encode("utf-8"), "count: ", count, ",".join(words)


def key_words_analysis(M, thresh, key_words):
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
	


f = open("/home/zhounan/corpus/events/tianjin")
N = len(key_words)
m = np.mat(np.zeros((N, N)))

for line in f:
	key_words_match(line, m, key_words)

C = key_words_analysis(m, 5, key_words)

for key in C:
	words = C[key]
	print ','.join(words)
