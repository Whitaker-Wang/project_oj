#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import shlex

import os
import lorun

import config
from db import get_data
from get_data import write_data
from judge_result import judge_result
# from main import low_level


def judge_one(id, question_id, data_num, time_limit, mem_limit, language, dblock):
    """评测一组数据"""
    # low_level()
    # 写入数据
    write_data(id, question_id)

    input_path = os.path.join(
        config.data_dir, str(question_id), 'data%s.in' % data_num)
    # print('use %s' % input_path)

    output_path = os.path.join(
        config.work_dir, str(id), 'out%s.txt' % data_num)

    try:
        input_data = open(input_path)
        # print('open input data')
        # print('success w')
    except:
        # print("False111")
        return False
    temp_out_data = open(output_path, 'w+')

    if language == 'java':
        cmd = 'java -cp %s Main' % (
            os.path.join(config.work_dir,
                         str(id)))
        main_exe = shlex.split(cmd)
    elif language == 'python2':
        cmd = 'python2 %s' % (
            os.path.join(config.work_dir,
                         str(id),
                         'main.pyc'))
        main_exe = shlex.split(cmd)
    elif language == 'python3':
        # print('python3')
        cmd = 'python3 %s' % (
            os.path.join(config.work_dir,
                         str(id),
                         '__pycache__/main.cpython-36.pyc'))
        main_exe = shlex.split(cmd)
    elif language == 'lua':
        cmd = "lua %s" % (
            os.path.join(config.work_dir,
                         str(id),
                         "main"))
        main_exe = shlex.split(cmd)
    elif language == "ruby":
        cmd = "ruby %s" % (
            os.path.join(config.work_dir,
                         str(id),
                         "main.rb"))
        main_exe = shlex.split(cmd)
    elif language == "perl":
        cmd = "perl %s" % (
            os.path.join(config.work_dir,
                         str(id),
                         "main.pl"))
        main_exe = shlex.split(cmd)
    else:
        main_exe = [os.path.join(config.work_dir, str(id), 'main'), ]
        # main_exe = shlex.split(main_exe)

    # in_path = os.path.join('/home/bri/project_oj/Judge/testdata', '4', 'data1.in')
    # out_path = os.path.join('/home/bri/project_oj/Judge/testdata', '4', 'data1.out')
    # fin = open(in_path)
    # ftemp = open('temp.out', 'w')
    # print('my input path:', input_path)
    # print('other input path:', in_path)
    # print("main_exe", main_exe)

    runcfg = {
        'args': main_exe,
        # 'args': ['cd', main_exe, '&&', 'java', 'Main'],
        'fd_in': input_data.fileno(),
        'fd_out': temp_out_data.fileno(),
        # 'fd_in':fin.fileno(),
        # 'fd_out':ftemp.fileno(),
        'timelimit': time_limit,  # in MS
        'memorylimit': mem_limit,  # in KB
    }
    # low_level()
    rst = lorun.run(runcfg)
    # print('lorun')
    input_data.close()
    temp_out_data.close()
    logging.debug(rst)
    # print(rst)
    # print('result', end=':  ')
    # print(judge_result(id, question_id, data_num))
    return rst


if __name__ == '__main__':
    judge_one(1, 4, 1, 200000, 700000, 'g++', None)
