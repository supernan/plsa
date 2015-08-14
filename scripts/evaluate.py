#coding=utf-8
import sys
import plsa as pl

if __name__ == '__main__':
        w2v_path = sys.argv[1]
	term_prob_path = sys.argv[2]
	dict_path = sys.argv[3]
	pl.evaluate(w2v_path, term_prob_path, dict_path)


