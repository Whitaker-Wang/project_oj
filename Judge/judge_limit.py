import logging
import shlex

import os

import config
from db import get_data
# from main import low_level


def judge_limit(id, question_id, data_num, time_limit, mem_limit, language, dblock):
    # low_level()
    """评测一组数据"""
    # 从数据库获取数据
    input_path = os.path.join(
        config.work_dir, str(question_id), 'data%s.in' % data_num)
    try:
        input_data = open(input_path, "a")
        data_list = get_data(question_id)
    except:
        return False

    output_path = os.path.join(
        config.work_dir, str(id), 'out%s.txt' % data_num)
    temp_out_data = open(output_path, 'w')
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
        cmd = 'python3 %s' % (
            os.path.join(config.work_dir,
                         str(id),
                         '__pycache__/main.cpython-33.pyc'))
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
    runcfg = {
        'args': main_exe,
        'fd_in': input_data.fileno(),
        'fd_out': temp_out_data.fileno(),
        'timelimit': time_limit,  # in MS
        'memorylimit': mem_limit,  # in KB
    }
    low_level()
    rst = lorun.run(runcfg)
    input_data.close()
    temp_out_data.close()
    logging.debug(rst)
    return rst

