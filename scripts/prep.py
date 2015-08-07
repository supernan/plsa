#coding=utf-8

import plsa as pl
import sys

if __name__ == '__main__':
	root_dir = sys.argv[1]
	dict_path = sys.argv[2]
	pl.preprocess(root_dir, dict_path)
