#!/usr/bin/env python
# coding=utf-8
import logging

import config
from data_dir import clean_work_dir
from db import run_sql, get_data_count, update_message
from run_code import run


def worker(q, dblock):
    """工作进程，循环扫描队列，获得评判任务并执行"""
    # print('start work')
    while True:
        # 获取任务，如果队列为空则阻塞
        task = q.get()
        # 获取题目信息
        id = task['id']
        content = task['content']
        question_id = task['question_id']
        language = task['language']
        user_id = task['user_id']
        # 评测
        data_count = get_data_count(task['question_id'])  # 获取测试数据的个数
        result_code = {
            "Waiting": 0,
            "Accepted": 1,
            "Time Limit Exceeded": 2,
            "Memory Limit Exceeded": 3,
            "Wrong Answer": 4,
            "Runtime Error": 5,
            "Output limit": 6,
            "Compile Error": 7,
            "Presentation Error": 8,
            "System Error": 11,
            "Judging": 12,
        }
        logging.info("judging %s" % question_id)
        result = run(
            question_id,
            id,
            language,
            data_count,
            user_id,
            dblock,
            result_code
        )  # 评判
        # print('worker\'s result')
        logging.info(
            "%s result %s" % (
                result[
                    'id'],
                result[
                    'result']))
        result_info = filter(lambda x: result['result'] == x[1], result_code.items())
        for key, value in result_info:
            result['result'] = key
        # print('updata message 1')
        # print(result)
        dblock.acquire()
        # 将结果写入数据库
        # print('updata message 2222')
        update_message(id, result)
        dblock.release()
        if config.auto_clean:  # 清理work目录
            # print('clean')
            clean_work_dir(result['id'])
        q.task_done()
