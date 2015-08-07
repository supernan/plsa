/*************************************************************************
 > File Name: plsa.h
 > Author: zhounan
 > Mail: scutzhounan@foxmail.com 
 > Created Time: 2015年07月26日 星期日 15时41分23秒
 ************************************************************************/

#include<iostream>
#include<map>
#include<math.h>
#include"util.h"
#include"const.h"
#include"tinyxml.h"
#include"tinystr.h"
#include<time.h>

#ifndef _PLSA_H_
#define _PLSA_H_

#define LM 18

namespace nlp
{
	static double _doc_probs[MAX_DOCS][MAX_TOPICS]; //文档属于某个主题的概率 PI
	static double _term_probs[MAX_TERMS][MAX_TOPICS]; //词属于某个主题的概率 P(w|j)
	static double _doc_term_probs[MAX_DOCS][MAX_TERMS][MAX_TOPICS]; //文档中的某个词属于某个主题的概率 Z(d,w)
	static double _counts[MAX_DOCS][MAX_TERMS]; //某个词在某篇文档中出现的个数 c(d,w)
	
	
	class Plsa
	{
		public:
			Plsa(std::string &conf_path);
			void train_plsa();
			void save_args(std::string &path);
		
		private:
			void _load_config(std::string &path);
			void _init_model();
			void _init_z_variable();
			void _calc_z_variable();
			void _calc_PI_variable();
			void _calc_term_prob();
			void _init_args();
			void _Estep();
			void _Mstep();

			tools::Util util;
			std::string _dict_path;
			std::string _doc_tf_path;

			int _docs_nums;
			int _terms_nums;
			int _topics_nums;
			int _iter_nums;
			std::map<int, double> _doc_words_map; //统计每篇文档中的总词汇数
			
			double _lambda; 
			std::map<int, double> _tfs_map; //词频

	};
}


#endif
