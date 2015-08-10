/*************************************************************************
 > File Name: ../src/util.cpp
 > Author: zhounan
 > Mail: scutzhounan@foxmail.com 
 > Created Time: 2015年07月26日 星期日 10时29分07秒
 ************************************************************************/

#include"util.h"

void tools::Util::_split_line(std::string &line, std::string &key, std::vector<std::string> &word_list)
{
	int pos = -1;
	int last_pos = 0;
	int key_size = key.length();
	int line_size = line.length();
	if (key_size == 0)
		LOG(ERROR) << "_split_line key size is 0" << std::endl;
	if (line_size == 0)
		LOG(ERROR) << "_split_line line size is 0" << std::endl;
	while (true)
	{
		pos = line.find(key, last_pos);
		if (pos == -1)
			break;
		std::string word = line.substr(last_pos, pos - last_pos);
		if (word != "")
			word_list.push_back(word);
		last_pos = pos + key_size;
	}
	std::string last_word = line.substr(last_pos);
	if (last_word != "")
		word_list.push_back(last_word);
}


void tools::Util::read_words_dict(std::string &path, std::map<int, double> &dict_tf)
{
	if ((access(path.c_str(), F_OK)) == -1)
		LOG(FATAL) << "dict path is wrong" << std::endl;
	std::ifstream input_stream(path.c_str());
	std::string line;
	int count = 0;
	while (getline(input_stream, line))
	{
		std::vector<std::string> parts;
		std::string key = " ";
		_split_line(line, key, parts);
		if (parts.size() < 3)
			LOG(FATAL) << "dict file format is wrong" <<" "<<"line: "<<count<< std::endl;
		int word_id = atoi(parts[0].c_str());
		double tf = atof(parts[2].c_str());
		dict_tf[word_id] = tf;
		count++;
	}
	terms_num = count;
}


void tools::Util::read_doc_tf(std::string &path, double counts[MAX_DOCS][MAX_TERMS],
		                      std::map<int, double> &doc_words_map, std::map<int, double> &dict_map)
{
	if ((access(path.c_str(), F_OK)) == -1)
		LOG(FATAL) << "doc path is wrong" << std::endl;
	std::ifstream input_stream(path.c_str());
	std::string line;
	docs_num = 0;
	while (getline(input_stream, line))
	{
		std::vector<std::string> parts;
		std::string first_key = " ";
		_split_line(line, first_key, parts);
		if (parts.size() != 2)
			LOG(FATAL) << "doc file format is wrong :parts size error" <<" "<<"line: "<<docs_num<< std::endl;
		int doc_id = atoi(parts[0].c_str());
		double total_words = 0;

		std::vector<std::string> records;
		std::string second_key = "|";
		_split_line(parts[1], second_key, records);

		for (int i = 0; i < records.size(); i++)
		{
			std::string third_key = ":";
			std::vector<std::string> tfs;
			_split_line(records[i], third_key, tfs);
			if (tfs.size() != 2)
				LOG(FATAL) << "doc file format is wrong :tfs size error" << std::endl;
			else
			{
				int term_id = atoi(tfs[0].c_str());
				double tf = atof(tfs[1].c_str());
				total_words += tf;

				std::map<int, double>::iterator iter;
				iter = dict_map.find(term_id);
				if (iter != dict_map.end())
					counts[doc_id][term_id] = tf;
			}

		}
		docs_num++;
		doc_words_map[doc_id] = total_words;
	}
}
