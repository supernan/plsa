#coding=utf-8
import plsa as pl
import sys

if __name__ == '__main__':
    test_dir = sys.argv[1]
    dict_path = sys.argv[2]
    term_prob_path = sys.argv[3]
    topic_num = int(sys.argv[4])
    pl.predict_test_files(dict_path, test_dir, term_prob_path, topic_num)
	
