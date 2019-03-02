#!/usr/bin/env python
# coding=utf-8
import os

import config
from db import update_message
# from main import low_level
import subprocess


def compile_code(id, language, dblock):
    """将程序编译成可执行文件"""
    # low_level()
    language = language.lower()
    dir_work = os.path.join(config.work_dir, str(id))
    build_cmd = {
        "gcc":
        "gcc main.c -o main -Wall -lm -O2 -std=c99 --static -DONLINE_JUDGE",
        "g++": "g++ main.cpp -O2 -Wall -lm --static -DONLINE_JUDGE -o main",
        "java": "javac Main.java",
        "ruby": "reek main.rb",
        "perl": "perl -c main.pl",
        "pascal": 'fpc main.pas -O2 -Co -Ct -Ci',
        "go": '/opt/golang/bin/go build -ldflags "-s -w"  main.go',
        "lua": 'luac -o main main.lua',
        "python2": 'python2 -m py_compile main.py',
        "python3": 'python3 -m py_compile main.py',
        "haskell": "ghc -o main main.hs",
    }
    if language not in build_cmd.keys():
        return False
    p = subprocess.Popen(
        build_cmd[language],
        shell=True,
        cwd=dir_work,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = p.communicate()  # 获取编译错误信息
    # err_txt_path = os.path.join(config.work_dir, str(id), 'error.txt')
    # f = file(err_txt_path, 'w')
    with open('%s/error.txt' % dir_work, 'wb+') as f:
        f.write(err)
        f.write(out)
        f.close()
    # print(p, end='p.returncoude===')
    # print(p.returncode)
    if p.returncode == 0:  # 返回值为0,编译成功
        return True
    # print((err + out).decode(encoding='utf-8'))
    # print(type(err))
    error_out = None
    try:
        error_out = "\'"+(err+out).decode(encoding='utf-8')+"\'"
    except:
        pass
    try:
        error_out = "\"" + (err + out).decode(encoding='GBK') + "\""
    except:
        pass
    # print(error_out, type(error_out))
    dblock.acquire()
    # print('error message(compile)')
    update_message(id, error_out)  # 编译失败,更新题目的编译错误信息
    dblock.release()
    return False

#
# if __name__ == '__main__':
#     # flag = compile_code(1, 'g++', None)
#     flag = compile_code(2, 'g++', None)
#     print(flag)