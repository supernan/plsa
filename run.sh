#########################################################################
# File Name: run.sh
# Author: zhounan
# mail: scutzhounan@foxmail.com
# Created Time: 2015年07月29日 星期三 17时18分30秒
#########################################################################
#!/bin/bash

PY_HOME=./scripts
PROJECT_HOME=/home/zhounan/project/ict/plsa/plsa
ROOT_DIR=/home/zhounan/corpus/events/sunyang_swimming #语料库文件夹地址
TRAIN_CORPUS=/home/zhounan/corpus/events/sunyang #语料文件
TEST_DIR=/home/zhounan/corpus/events #测试语料地址
STOP_WORDS_PATH=/home/zhounan/corpus/stop_words #停用词表地址
DICT_PATH=$PROJECT_HOME/data/event_words_tf #生成的字典地址
TRAIN_FILE_PATH=$PROJECT_HOME/data/event_doc_word2 #训练数据地址
TRAIN_PATH=$PROJECT_HOME/build/ #训练程序路径
DOC_PLSA=$PROJECT_HOME/data/doc_probs #PLSA文档话题分布
TERM_PLSA=$PROJECT_HOME/data/term_probs #PLSA词项话题分布
TOPIC_NUM=8 #话题数
TOPIC_ID=1 #要查看的话题id
RESULT_PATH=$PROJECT_HOME/data #存储展示结果的路径

function gen_dict()
{
	cd $PY_HOME
	echo `pwd`
	python gen_dict.py $ROOT_DIR $STOP_WORDS_PATH > $DICT_PATH
}	


function prep()
{
	cd $PY_HOME
	echo `pwd`
	python prep.py $TRAIN_CORPUS $DICT_PATH > $TRAIN_FILE_PATH
}


function train()
{
	cd $TRAIN_PATH
	echo `pwd`
	./plsa_train
}


function show_topic_docs()
{
	cd $PY_HOME
	echo `pwd`
	python show_result.py $TRAIN_CORPUS $DOC_PLSA $TOPIC_NUM $TOPIC_ID > $RESULT_PATH/${TOPIC_ID}_docs
}


function show_topic_words()
{
	cd $PY_HOME
	echo `pwd`
	python topic_words.py $TERM_PLSA $DICT_PATH > $RESULT_PATH/topic_words
}


function predict_topic()
{
	cd $PY_HOME
	echo `pwd`
	python predict.py $TEST_DIR $DICT_PATH $TERM_PLSA $TOPIC_NUM
}


################### main function ######################
	while getopts "gptswk" arg
	echo $arg
	do
		case $arg in 
			g)
				echo "生成词典"
				gen_dict
				break
				;;
			p)
				echo "预处理"
				prep
				break
				;;
			t)
				echo "训练PLSA"
				train
				break
				;;
			s)
				echo "展示聚类结果"
				show_topic_docs
				break
				;;
			w)
				echo "展示话题中心词"
				show_topic_words
				break
				;;
			k)
				echo "文档话题预测"
				predict_topic
				break
				;;
			?)
				echo "请按照以下参数执行"
				echo "-g 依据语料生成词典"
				echo "-p 预处理语料生成训练数据"
				echo "-t 训练PLSA模型"
				echo "-s 展示训练数据的聚类效果"
				echo "-w 展示每个话题的中心词"
				echo "-k 预测文档的话题分类"
				echo "运行前需要配置脚本中的参数！"
				break
				;;
		esac
	done

