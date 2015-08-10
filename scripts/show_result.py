#coding=utf-8
import sys
import plsa as pl

if __name__ == '__main__':
	root_dir = sys.argv[1]
	plsa_path = sys.argv[2]
	topic_num = int(sys.argv[3])
	topic_id = int(sys.argv[4])
	print topic_num, topic_id
	pl.show_topics(root_dir, plsa_path, topic_num, topic_id)
