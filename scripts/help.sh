#########################################################################
# File Name: help.sh
# Author: zhounan
# mail: scutzhounan@foxmail.com
# Created Time: 2015年07月24日 星期五 08时48分20秒
#########################################################################
#!/bin/bash

ROOT_DIR="/home/zhounan/corpus/sogou_total"
NEW_DIR="/home/zhounan/corpus/sogou_part"
F_ENCODING="gb18030"
T_ENCODING="utf-8"


function encoding_change(){
	
	for dir in `ls $ROOT_DIR`
	do
		if [ -d $ROOT_DIR/$dir ]
		then
			for file in `ls $ROOT_DIR/$dir`
			do
	#			echo $ROOT_DIR/$dir/$file
				if [ -e $ROOT_DIR/$dir/$file ]
				then
					iconv -f $F_ENCODING -t $T_ENCODING $ROOT_DIR/$dir/$file -o $ROOT_DIR/$dir/${file}_utf8
				fi
			done
		fi
	done

}

function partition_data(){
	
	for dir in `ls $ROOT_DIR`
	do
		if [ -d $ROOT_DIR/$dir ]
		then
			mkdir $NEW_DIR/$dir
			count=0
			for file in `ls $ROOT_DIR/$dir`
			do
				((count++))
				echo $count
				echo $ROOT_DIR/$dir/$file
				if [ -e $ROOT_DIR/$dir/$file ]
				then
					cp $ROOT_DIR/${dir}/$file $NEW_DIR/${dir}/$file 
				fi
				if [ $count -gt 100 ]
				then
					break
				fi
			done
		fi
	done
	
}

function file_count(){
	
	count=0
	for dir in `ls $ROOT_DIR`
	do
		if [ -d $ROOT_DIR/$dir ]
		then
			for file in `ls $ROOT_DIR/$dir`
			do
				if [ -e $ROOT_DIR/$dir/$file ]
				then
					((count++))
				fi
			done
		fi
	done
	echo $count
	
}


#encoding_change
partition_data
#file_count
