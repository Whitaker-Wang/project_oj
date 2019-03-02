#!/usr/bin/env python
# coding=utf-8
import logging

from check_code import check_dangerous_code
from compile_code import compile_code
from db import get_limit
from judge_code import judge
# from main import low_level


def run(question_id, id, language, data_count, user_id, dblock, result_code):
    # low_level()
    """获取程序执行时间和内存"""
    dblock.acquire()
    time_limit, mem_limit = get_limit(question_id)
    dblock.release()
    program_info = {
        "id": id,
        "question_id": question_id,
        "take_time": 0,
        "take_memory": 0,
        "user_id": user_id,
        "result": 0,
    }
    if check_dangerous_code(id, language) is False:
        program_info['result'] = result_code["Runtime Error"]
        return program_info
    # print('start compile')
    compile_result = compile_code(id, language, dblock)
    # print('compile :' ,end='')
    # print('123213123',compile_result)
    if compile_result is False:  # 编译错误
        program_info['result'] = result_code["Compile Error"]
        return program_info
    if data_count == 0:  # 没有测试数据
        program_info['result'] = result_code["System Error"]
        return program_info
    result = judge(
        id,
        question_id,
        data_count,
        time_limit,
        mem_limit,
        program_info,
        result_code,
        language,
        dblock
    )
    # print(result, end=' ')
    # print('retrun to worker')
    logging.debug(result)
    return result
