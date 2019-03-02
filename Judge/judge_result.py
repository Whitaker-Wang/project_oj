#!/usr/bin/env python
# coding=utf-8
import logging

import os

import config
# from Judge.db import get_data
# from main import low_level


def judge_result(id, question_id, data_num):
    # low_level()
    '''对输出数据进行评测'''
    # print('judge result ')
    logging.debug("Judging result")
    # all_data = get_data(question_id)
    # print(all_data)
    correct_result = os.path.join(
        config.data_dir, str(question_id), 'data%s.out' %
        data_num)
    user_result = os.path.join(
        config.work_dir, str(id), 'out%s.txt' %
        data_num)
    correct_file = open(correct_result, 'r')
    user_file = open(user_result, 'r')
    try:
        correct = correct_file.read().replace('\r', '').rstrip()  # 删除\r,删除行末的空格和换行
        user = user_file.read().replace('\r', '').rstrip()
        # print("correct:", correct)
        # print("user:", user)
        correct_file.close()
        user_file.close()
    except:
        return False
    if correct == user:  # 完全相同:AC
        return "Accepted"
    if correct.split() == user.split():  # 除去空格,tab,换行相同:PE
        return "Presentation Error"
    if correct in user:  # 输出多了
        return "Output limit"
    return "Wrong Answer"  # 其他WA

# if __name__ == '__main__':
#     judge_result(0,1,1)


