#coding=utf-8
import plsa as pl
import sys

#root_dir = "/home/zhounan/corpus/sogou_part"
#stop_words_path="/home/zhounan/corpus/stop_words"

if __name__ == '__main__':
	root_dir = sys.argv[1]
	stop_words_path = sys.argv[2]
	pl.generate_words_dict(root_dir, stop_words_path)
