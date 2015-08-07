#coding=utf-8
import sys
import plsa as pl

if __name__ == '__main__':
	term_prob_path = sys.argv[1]
	dict_path = sys.argv[2]
	pl.get_topic_words(term_prob_path, dict_path)


