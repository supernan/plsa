#coding=utf-8
import jieba
import os
import sys
import math

#train_set = []
#root_dir = "/home/zhounan/corpus/sogou_part"
#stop_words_path="/home/zhounan/corpus/stop_words"
#dict_path = "words_tf"
#words_dict = dict()
#stop_words = []


def load_dict(path):
	"""
	加载词典
	"""
	f = open(path)
	words_dict = dict()
	for line in f:
		parts = line.strip().split(" ")
		words_dict[parts[1]] = int(parts[0])
	return words_dict


def load_stop_words(path):
	"""
	加载停用词
	"""
	f = open(path)
	stop_words = []
	for line in f:
		stop_words.append(line.strip())
	return stop_words


def load_single_file(path, words_dict, stop_words):
	"""
	读取单独一个文件 统计词频
	"""
	f = open(path)
	raw_text = f.read()
	word_list = list(jieba.cut(raw_text, cut_all = False))
	for word in word_list:
		if word.encode("utf-8") in stop_words:
			continue
		if words_dict.has_key(word):
			words_dict[word] += 1
		else:
			words_dict[word] = 1


def load_train_set(root_dir, stop_words_path):
	"""
	读取语聊集合生成词典，统计词频
	"""
	stop_words = load_stop_words(stop_words_path)
	words_dict = dict()
	for parent, dirs, files in os.walk(root_dir):
		for filename in files:
			load_single_file(os.path.join(parent, filename), words_dict, stop_words)
	return words_dict


def encode_words_dict(words_dict):
	"""
	将字典和词频统计结果编码成指定格式并输出
	"""
	count = 0
	word_list = []
	id_list = []
	tf_list = []
	total = 0.0
	sorted_list = sorted(words_dict.iteritems(), key=lambda d:d[1], reverse = True)
	for word_tuple in sorted_list:
		id_list.append(count)
		word_list.append(word_tuple[0].encode("utf-8"))
		tf_list.append(float(word_tuple[1]))
		total += float(word_tuple[1])
		count += 1
	for i in range(len(id_list)):
		print id_list[i], word_list[i], float(tf_list[i] / total)


def generate_words_dict(root_dir, stop_words_path):
	"""
	读取语聊生成词典，并输出
	"""
	words_dict = load_train_set(root_dir, stop_words_path)
	encode_words_dict(words_dict)


def dict2str(doc_dict, words_dict):
	"""
	将文本统计结果转化成指定格式的字符串
	"""
	ret = ""
	for word in doc_dict:
		word_id = words_dict[word]
		ret += str(word_id)
		ret += ":"
		ret += str(doc_dict[word])
		ret += "|"
	return ret


def process_single_file(path, words_dict):
	"""
	预处理单独的文件，返回文档tf统计
	"""
	f = open(path)
	raw_text = f.read()
	doc_dict = dict()
	word_list = list(jieba.cut(raw_text, cut_all = False))
	for word in word_list:
		word_key = word.encode("utf-8")
		if words_dict.has_key(word_key):
			if doc_dict.has_key(word_key):
				doc_dict[word_key] += 1
			else:
				doc_dict[word_key] = 1
	return doc_dict


def process_train_set(root_dir, dict_path):
	"""
	预处理训练预料，生成训练数据
	"""
	count = 0
	words_dict = load_dict(dict_path)
	for parent, dirs, files in os.walk(root_dir):
		for filename in files:
			doc_dict = process_single_file(os.path.join(parent, filename), words_dict)
			doc_str = dict2str(doc_dict, words_dict)
			print count, doc_str
			count += 1


def preprocess(root_dir, dict_path):
	"""
	预处理训练数据
	"""
	process_train_set(root_dir, dict_path)


def extract_docs(root_dir, doc_list):
	"""
	抽取文档集合中的内容
	"""
	count = 0
	for parent, dirs, files in os.walk(root_dir):
		for filename in files:
			if count in doc_list:
				extract_single_doc(os.path.join(parent, filename))
			count += 1


def extract_single_doc(path):
	"""
	抽取文档中的内容
	"""
	f = open(path)
	raw_text = f.read()
	text = ''.join(raw_text.split())
	print text.strip()


def handle_plsa_result(path, topic_num):
	"""
	将训练文本划分到对应话题
	"""
	f = open(path)
	topic_dict = dict()
	for i in range(topic_num):
		doc_list = []
		topic_dict[i] = doc_list
        count = 0
	for line in f:
		parts = line.strip().split(" ")
                parts = parts[1:]
		max_prob = float(parts[0])
		max_topic = 0
		for i in range(len(parts)):
			prob = float(parts[i])
			if prob > max_prob:
				max_prob = prob
				max_topic = i
                print max_topic
		topic_dict[max_topic].append(count)
                count += 1
	return topic_dict


def show_topics(root_dir, plsa_path, topic_num, topic):
	"""
	展示某个话题的聚类效果
	"""
	topic_dict = handle_plsa_result(plsa_path, topic_num)
	doc_list = topic_dict[topic]
	if len(doc_list) > 0:
		extract_docs(root_dir, doc_list)


def get_topic_words(term_probs_path, dict_path):
	"""
	展现每个话题的高频词
	"""
	dict_f = open(dict_path)
	term_prob_f = open(term_probs_path)
	words_dict = dict()
	for line in dict_f:
		parts = line.strip().split(" ")
		wid = int(parts[0])
		word = parts[1]
		words_dict[wid] = word
	
	topic_dict = dict()
	is_first_line = True
	line_num = 0
	for line in term_prob_f:
		parts = line.strip().split(" ")
                parts = parts[1:]
		if is_first_line:
			topics = len(parts)
			for i in range(topics):
				term_dict = dict()
				topic_dict[i] = term_dict
			is_first_line = False

		for i in range(len(parts)):
			prob = float(parts[i])
			topic_dict[i][words_dict[line_num]] = prob
		line_num += 1
	
	for topic_id in topic_dict:
		topic_sorted= sorted(topic_dict[topic_id].iteritems(), key=lambda d:d[1], reverse = True)[:10]
		top_words = []
		for t in topic_sorted:
			top_words.append(str(t[0]) + ":" + str(t[1]))
		print ' '.join(top_words)


def read_test_files(root_dir):
	"""
	读取测试文件
	"""
	text_list = []
	for parent, dirs, files in os.walk(root_dir):
		for filename in files:
			f = open(os.path.join(parent, filename))
			text_list.append(f.read())
	return text_list


def get_words_list(words_dict, raw_text):
	"""
	将文本分词并选出在词典中出现的词
	"""
	key_words = []
	word_list = list(jieba.cut(raw_text, cut_all = False))
	for word in word_list:
		if words_dict.has_key(word.encode("utf-8")):
			key_words.append(word.encode("utf-8"))
	return key_words


def get_term_probs(path):
	"""
	读取词项-主题概率
	"""
	f = open(path)
	terms_dict = dict()
	for line in f:
		tid = 0
		probs = []
		parts = line.strip().split(" ")
		for i in range(len(parts)):
			if i == 0:
				tid = int(parts[i])
			else:
				prob = float(parts[i])
				probs.append(prob)
		terms_dict[tid] = probs
	return terms_dict


def calc_likelihood(words_dict, terms_dict, key_words, topic_num):
	"""
	计算要预测文本关键词针对每一个主题的似然函数
	"""
	likelihood_probs = dict()
	for i in range(topic_num):
		prob = 0.0
		for word in key_words:
			tid = words_dict[word]
			probs = terms_dict[tid]
			if probs[i] == 0:
				probs[i] = 1e-100
			prob += math.log(probs[i])
		likelihood_probs[i] = prob
	return likelihood_probs


def generate_prior(topic_num):
	"""
	为每个话题生成先验概率
	"""
	prior_probs = dict()
	for i in range(topic_num):
		prior_probs[i] = float(1) / float(topic_num)
	return prior_probs


def calc_posterior(likelihood_probs, prior_probs, topic_num):
	"""
	计算每个话题的后验概率
	"""
	post_probs = dict()
	for i in range(topic_num):
		prob = likelihood_probs[i] + math.log(prior_probs[i])
		post_probs[i] = prob
	return post_probs


def predict_test_files(dict_path, root_dir, term_probs_path, topic_num):
	"""
	预测文档属于哪一个主题
	"""
	words_dict = load_dict(dict_path)
	text_list = read_test_files(root_dir)
	terms_dict = get_term_probs(term_probs_path)
	for raw_text in text_list:
		key_words = get_words_list(words_dict, raw_text)
		likelihood = calc_likelihood(words_dict, terms_dict, key_words, topic_num)
		prior = generate_prior(topic_num)
		post = calc_posterior(likelihood, prior, topic_num)
		for topic_id in post:
			print topic_id, post[topic_id]
		print






		


				




	

#get_topic_words("/home/zhounan/develop/cpp/plsa/data/term_probs", "/home/zhounan/develop/cpp/plsa/data/words_tf")
#generate_words_dict()
#show_topics(root_dir, "doc_probs", 10, 3)
#process_train_set(root_dir)
#for w in words_dict:
#	print w.encode("utf-8"),words_dict[w]
#load_single_file("/home/zhounan/corpus/sogou/C000008/1571.txt_utf8")
#generate_model()
#total_dict = corpora.Dictionary.load("total_dict")

#encode_words_dict("words_part_dict")
