#!/usr/bin/env python
# coding=utf-8
import codecs
import logging
import os

import config
# from main import low_level
from db import get_data, get_data_count


def write_data(id, question_id):
    """从数据库获取数据并写入data_dir目录下对应的文件"""
    try:
        data_path = os.path.join(config.data_dir, str(question_id))
        # low_level()
        os.mkdir(data_path)
    except OSError as e:
        if str(e).find("exist" or "已存在") > 0:  # 文件夹已经存在
            # return
            # print('exist')
            return False
        else:
            logging.error(e)
            return False
    # print('hello')
    data_num = get_data_count(question_id)
    # print(data_num)
    all_data = get_data(question_id)
    for data in all_data:
        try:
            in_path = os.path.join(
                config.data_dir,
                str(question_id), 'data%s.in' % data_num)
            out_path = os.path.join(
                config.data_dir,
                str(question_id), 'data%s.out' % data_num)
        except KeyError as e:
            logging.error(e)
            return False
        try:
            # low_level()
            f_in = codecs.open(in_path, 'a')
            f_out = codecs.open(out_path, 'a')
            # print('already open')
            try:
                # print('start write')
                # print(all_data)
                # print(data, data[2])
                f_in.write(data[1]+"\n")
                f_out.write(data[3]+"\n")
            except:
                logging.error("%s not write data to file" % question_id)
                f_in.close()
                f_out.close()
                return False
            f_in.close()
            f_out.close()
        except OSError as e:
            logging.error(e)
            return False
        data_num = data_num - 1
    # print('success')
    return True


if __name__ == '__main__':
    write_data(2, 3)
