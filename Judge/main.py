#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

import sys

from multiprocessing import Process, Manager
from multiprocessing.pool import Pool

import time

# from Judge.worker import worker
from worker import worker
# from Judge.producer import producer
from producer import producer

# print('hello')

def low_level():
    """进行权限限制,设置为nobody用户"""
    try:
        os.setuid(int(os.popen("id -u %s" % "nobody").read()))
    except:
        pass


try:
    # 降低程序运行权限，防止恶意代码
    os.setuid(int(os.popen("id -u %s" % "nobody").read()))
except:
    logging.error("please run this program as root!")
    sys.exit(-1)


def start_product(pool, q, lock):
    """开始生产进程"""
    pool.apply_async(func=producer, args=(q, lock))


def start_work(q, lock, pool):
    """"开始工作进程"""
    for i in range(4):
        pool.apply_async(func=worker, args=(q, lock))


def check_process(pool, q, lock):
    """检查工作进程是否正常工作"""
    low_level()
    while True:
        time.sleep(60)
        pool.apply_async(func=worker, args=(q, lock))


def start_check_process(pool, q, lock):
    """开始检查功能的守护进程"""
    low_level()
    check_process(pool, q, lock)


def main():
    low_level()
    q = Manager().Queue(10)
    lock = Manager().Lock()
    size = 5
    pool = Pool(processes=size)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s --- %(message)s', )
    start_product(pool, q, lock)
    start_work(q, lock, pool)
    start_check_process(pool, q, lock)
    pool.close()
    pool.join()


if __name__ == '__main__':
    # from Judge.worker import worker
    # from Judge.producer import producer
    main()
# main()
