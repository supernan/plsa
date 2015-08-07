/*************************************************************************
 > File Name: util.h
 > Author: zhounan
 > Mail: scutzhounan@foxmail.com 
 > Created Time: 2015年07月26日 星期日 10时11分19秒
 ************************************************************************/

#include<iostream>
#include<fstream>
#include<map>
#include<vector>
#include<stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include"const.h"
#include "glog/logging.h"
#ifndef _UTIL_H_
#define _UTIL_H_

namespace tools
{
	class Util
	{
		public:
			int docs_num;
			int terms_num;
			void read_words_dict(std::string &dict_path, std::map<int, double> &dict_tf);
			void read_doc_tf(std::string &doc_path, double counts[MAX_DOCS][MAX_TERMS],
					         std::map<int, double> &doc_words_map, std::map<int, double> &dict_tf);
		private:
			void _split_line(std::string &line, std::string &key, std::vector<std::string> &words_list);
	};
}

#endif

