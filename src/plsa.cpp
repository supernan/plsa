/*************************************************************************
 > File Name: ../src/plsa.cpp
 > Author: zhounan
 > Mail: scutzhounan@foxmail.com 
 > Created Time: 2015年07月26日 星期日 16时06分53秒
 ************************************************************************/

#include"plsa.h"

void nlp::Plsa::_load_config(std::string &path)
{
	if ((access(path.c_str(), F_OK)) == -1)
		LOG(FATAL) << "config path is wrong" << std::endl;

	TiXmlDocument *plsa_config = new TiXmlDocument(path.c_str());
	plsa_config->LoadFile(); 
	TiXmlElement *root_element = plsa_config->RootElement();
	TiXmlElement *topic_node = root_element->FirstChildElement();
	TiXmlElement *iter_node = topic_node->NextSiblingElement();
	TiXmlElement *lambda_node = iter_node->NextSiblingElement();
	TiXmlElement *dict_node = lambda_node->NextSiblingElement();
	TiXmlElement *doc_node = dict_node->NextSiblingElement();

	std::string topics_str = topic_node->FirstChild()->Value();
	std::string iters_str = iter_node->FirstChild()->Value();
	std::string lambda_str = lambda_node->FirstChild()->Value();
	std::string dict_path_str = dict_node->FirstChild()->Value();
	std::string doc_path_str = doc_node->FirstChild()->Value();

	_topics_nums = atoi(topics_str.c_str());
	_iter_nums = atoi(iters_str.c_str());
	_lambda = atof(lambda_str.c_str());
	_dict_path = dict_path_str;
	_doc_tf_path = doc_path_str;

	delete plsa_config;
}


void nlp::Plsa::_init_model()
{
	LOG(INFO) << "init plsa model" << std::endl;
	for (int i = 0; i < MAX_DOCS; i++)
	{
		for (int j = 0; j < MAX_TERMS; j++)
		{
			_counts[i][j] = 0.0;
			for (int k = 0; k < MAX_TOPICS; k++)
			{
				_doc_probs[i][k] = 0.0;
				_term_probs[j][k] = 0.0;
				_doc_term_probs[i][j][k] = 0.0;
			}
		}
	}

	util.read_words_dict(_dict_path, _tfs_map);
	util.read_doc_tf(_doc_tf_path, _counts, _doc_words_map, _tfs_map);
	_terms_nums = util.terms_num;
	_docs_nums = util.docs_num;
}

nlp::Plsa::Plsa(std::string &conf_path)
{
	_load_config(conf_path);
	_init_model();
}


void nlp::Plsa::_init_z_variable()
{
	LOG(INFO) << "init latent variable z" << std::endl;
	srand(time(0));
	LOG(INFO) <<_docs_nums<<" "<<_topics_nums<<" "<<_terms_nums<<std::endl;
	clock_t start,finish;
	double total_time = 0.0;
	start=clock();
	for (int i = 0; i < _docs_nums; i++)
	{
		for (int j = 0; j < _terms_nums; j++)
		{
			double lm_prob = double(_counts[i][j]) / double(_doc_words_map[i]);
			_doc_term_probs[i][j][LM] = lm_prob;
			std::vector<int> random_nums;
			int total = 0;
			for (int k = 0; k < _topics_nums; k++)
			{
				int num = rand()%100;
				random_nums.push_back(num);
				total += num;
			}
			for (int k = 0; k < _topics_nums; k++)
			{
				double prob = double(random_nums[k]) / double(total);
				_doc_term_probs[i][j][k] = prob;
			}
		}
	}
	finish = clock();
	total_time=(double)(finish-start)/CLOCKS_PER_SEC;
	LOG(INFO) <<"init z finish"<<" "<<total_time<<"s" <<std::endl;

}


void nlp::Plsa::_calc_z_variable()
{
	LOG(INFO) <<"calc z"<<std::endl;
	clock_t start,finish;
	double total_time = 0.0;
	start=clock();
	for (int i = 0; i < _docs_nums; i++)
	{
		for (int j = 0; j < _terms_nums; j++)
		{
			double topic_sum = 0.0;
			for (int k = 0; k < _topics_nums; k++)
			{
				double prob = _doc_probs[i][k] * _term_probs[j][k];
				_doc_term_probs[i][j][k] = prob;
				//std::cout<<k<<" "<<prob<<std::endl;
				topic_sum += prob;
			}
			for (int k = 0; k < _topics_nums; k++)
			{
				if (_doc_term_probs[i][j][k] != 0)
					_doc_term_probs[i][j][k] /= topic_sum;
			}
			double lm_prob = _tfs_map[j];
			_doc_term_probs[i][j][LM] = (_lambda * lm_prob) / (_lambda * lm_prob + (1 - _lambda) * topic_sum);
		}
	}
	finish = clock();
	total_time=(double)(finish-start)/CLOCKS_PER_SEC;
	LOG(INFO) <<"calc z finish"<<" "<<total_time<<"s"<<std::endl;

}


void nlp::Plsa::_calc_PI_variable()
{
	LOG(INFO) <<"calc pi"<<std::endl;
	clock_t start,finish;
	double total_time = 0.0;
	start=clock();
	for (int i = 0; i < _docs_nums; i++)
	{
		double topic_sum = 0.0;
		for (int k = 0; k < _topics_nums; k++)
		{
			double term_sum = 0.0;
			for (int j = 0; j < _terms_nums; j++)
			{
				term_sum += _counts[i][j] * (1 - _doc_term_probs[i][j][LM]) * _doc_term_probs[i][j][k];
			}
			_doc_probs[i][k] = term_sum;
			//std::cout<<_doc_probs[i][k]<<std::endl;
			topic_sum += term_sum;
		}
		for (int k = 0; k < _topics_nums; k++)
		{
			if (_doc_probs[i][k] != 0)
				_doc_probs[i][k] /= topic_sum;
			//std::cout<<"doc_prob"<<" "<<i<<" "<<k<<" "<<_doc_probs[i][k]<<std::endl;
		}

	}
	finish = clock();
	total_time=(double)(finish-start)/CLOCKS_PER_SEC;
	LOG(INFO)<<"calc pi finish"<<" "<<total_time<<"s"<<std::endl;
}


void nlp::Plsa::_calc_term_prob()
{
	LOG(INFO) <<"calc term prob"<<std::endl;
	clock_t start,finish;
	double total_time = 0.0;
	start=clock();
	for (int k = 0; k < _topics_nums; k++)
	{
		double term_sum = 0.0;
		for (int j = 0; j < _terms_nums; j++)
		{
			double doc_sum = 0.0;
			for (int i = 0; i < _docs_nums; i++)
			{
				doc_sum += _counts[i][j] * (1 - _doc_term_probs[i][j][LM]) * _doc_term_probs[i][j][k];
			}
			term_sum += doc_sum;
			_term_probs[j][k] = doc_sum;
		}
		for (int j = 0; j < _terms_nums; j++)
		{
			if (_term_probs[j][k] != 0)
				_term_probs[j][k] /= term_sum;
			//std::cout<<"term "<<j<<" "<<k<<" "<<_term_probs[j][k]<<std::endl;
		}
	}
	finish = clock();
	total_time=(double)(finish-start)/CLOCKS_PER_SEC;
	LOG(INFO) <<"calc term finish"<<" "<<total_time<<"s"<<std::endl;
}


void nlp::Plsa::_init_args()
{
	_init_z_variable();
	_calc_PI_variable();
	_calc_term_prob();
}


void nlp::Plsa::_Estep()
{
	_calc_z_variable();
}


void nlp::Plsa::_Mstep()
{
	_calc_PI_variable();
	_calc_term_prob();
}


void nlp::Plsa::train_plsa()
{
	_init_args();
	for (int i = 0; i < _iter_nums; i++)
	{
		LOG(INFO) <<i<<"th iteration"<<std::endl;
		_Estep();
		_Mstep();
	}
	std::string save_path = "../data";
	save_args(save_path);
}


void nlp::Plsa::save_args(std::string &path)
{
	std::string term_path = path + "/term_probs";
	std::string doc_path = path + "/doc_probs";

	std::ofstream term_out(term_path.c_str());
	std::ofstream doc_out(doc_path.c_str());

	for (int i = 0; i < _terms_nums; i++)
	{
		term_out<<i<<" ";
		for (int k = 0; k < _topics_nums; k++)
		{
			term_out<<_term_probs[i][k]<<" ";
		}
		term_out<<std::endl;
	}
	for (int i = 0; i < _docs_nums; i++)
	{
		doc_out<<i<<" ";
		for (int k = 0; k < _topics_nums; k++)
		{
			doc_out<<_doc_probs[i][k]<<" ";
		}
		doc_out<<std::endl;
	}
	term_out.close();
	doc_out.close();
}
