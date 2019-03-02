#!/usr/bin/env python
# coding=utf-8
import logging

import pymysql
import time
from pymysql import OperationalError


def run_sql(sql):
    """执行sql语句,并返回结果"""
    con = None
    while True:
        try:
            con = pymysql.connect(host='192.168.106.134', port=3306, user='root', password='1059291245',
                                  db='oj', charset='utf8')
            # print('connect success')
            break
        except Exception as e:
            logging.error('Cannot connect to database,trying again')
            logging.error(e)
            time.sleep(1)
    cur = con.cursor()
    try:
        if isinstance(sql, str):
            cur.execute(sql)
        elif isinstance(sql, list):
            for i in sql:
                cur.execute(i)
    except OperationalError as e:
        logging.error(e)
        cur.close()
        con.close()
        return False
    con.commit()
    data = cur.fetchall()
    cur.close()
    con.close()
    return data


def get_message():
    """获得操作结果信息"""
    sql = 'select * from submission where message = "waiting" '
    # print(sql%restrict)
    # print(sql)
    return run_sql(sql)


def update_message(id, msg):
    """更改信息"""
    sql = 'update submission set message = "{msg}" where id = {id}'
    # print(sql.format(msg=msg, id=id))
    return run_sql(sql.format(msg=msg, id=id))


def get_limit(qid):
    """获得限制信息"""
    sql = "select time_limit, mem_limit from data where que_id=%s"
    return list(run_sql(sql % qid)[0])


def get_data_count(quesion_id):
    """获得测试数据的个数信息"""
    sql = "select count(*) from data where que_id = %s"
    return run_sql(sql % quesion_id)[0][0]


def get_data(qid):
    """获得测试数据"""
    sql = "select * from data where que_id = %s"
    return run_sql(sql % qid)


# if __name__ == '__main__':
    # a = get_limit(1)
    # print(a)
    # a = get_data_count(1)
    # print(a)
    # print(type(a))
    # a = update_message(3, {'1223':1, "123":4234, 'result':14523} )
    # data = get_message()
    # print('hello')
    # print(data)

    # sql = "update submission set message = {msg} where id = {id}".format(msg='\"'+"erro"+'\"', id="1")
    # a = run_sql(sql)
    # print(a)
    # b = get_message("Null")
    # print(b)
    # a = get_data(1)
    # print(a)

