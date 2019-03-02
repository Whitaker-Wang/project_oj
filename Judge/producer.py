#!/usr/bin/env python
# coding=utf-8
import time

from data_dir import clean_work_dir
from db import run_sql, get_message, update_message
from get_code import get_code


def producer(q, dblock):
    """循环扫描数据库,将任务添加到队列"""
    # print('start produce')
    while True:
        if q.full():
            q.join()
        dblock.acquire()
        data = get_message()
        # print('-----')
        # print(data)
        # print('-----')
        time.sleep(0.5)   # 延时1秒,防止因速度太快不能获取代码
        dblock.release()
        for i in data:
            id, language, content, message, user_id, question_id = i
            dblock.acquire()
            ret = get_code(id, question_id, language, content)
            dblock.release()
            if ret is False:
                # 防止因速度太快不能获取代码
                time.sleep(1)
                dblock.acquire()
                ret = get_code(id, question_id, language, content)
                dblock.release()
            if ret is False:
                dblock.acquire()
                # 标记题目写入处理的结果信息'unknown error'写入数据库
                # run_sql("update submission set message = 'unknown error' where id = %s" % id)
                update_message(id, 'unknown error')
                dblock.release()
                clean_work_dir(id)
                continue
            # 标记题目写入处理的结果信息'success'写入数据库
            # run_sql("update submission set message = 'success' where id = %s" % id)
            update_message(id, "'The problem is being dealt with...'")
            # print('upmes2suc')
            task = {
                "id": id,
                "user_id": user_id,
                "question_id": question_id,
                "content": content,
                "language": language,
            }
            q.put(task)
        time.sleep(3)
