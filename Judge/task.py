#!/usr/bin/env python
# coding=utf-8
import time

from multiprocessing import Manager
from multiprocessing.pool import Pool

from data_dir import clean_work_dir
from db import run_sql
from get_code import get_code
# from Judge.main import low_level

def start_product(pool, q, lock):
    """开始生产进程"""
    pool.apply_async(func=producer, args=(q, lock))
def producer(q, dblock):
    """循环扫描数据库,将任务添加到队列"""
    # print("start")
    while True:
        if q.full():
            q.join()
        dblock.acquire()
        data = run_sql('select * from submission where message is NULL')
        # print(data)
        time.sleep(0.5)   # 延时1秒,防止因速度太快不能获取代码
        dblock.release()
        for i in data:
            id, language, content, message, user_id, question_id = i
            dblock.acquire()
            # print('1 put')
            ret = get_code(id, question_id, language, content)
            dblock.release()
            # print(ret)
            if ret is False:
                # 防止因速度太快不能获取代码
                # print('2 put')
                time.sleep(1)
                dblock.acquire()
                ret = get_code(id, question_id, language, content)
                dblock.release()
            if ret is False:
                dblock.acquire()
                # 标记题目写入处理的结果信息
                run_sql("update submission set message = 'unknown error' where id = %s"%id)
                dblock.release()
                clean_work_dir(id)
                continue
            run_sql("update submission set message = 'success' where id = %s" % id)
            task = {
                "id": id,
                "user_id": user_id,
                "question_id": question_id,
                "content": content,
                "language": language,
            }
            q.put(task)
        time.sleep(0.5)


def main():
    # low_level()
    q = Manager().Queue(10)
    lock = Manager().Lock()
    size = 5
    pool = Pool(processes=size)
    start_product(pool, q, lock)
    # start_work(q, lock, pool)
    # pool.apply_async(func=producer, args=(q, lock))
    # start_check_process(pool, q, lock)
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
# def hello():
#     print('hello')
#
# # if __name__ == '__main__':
# hello()