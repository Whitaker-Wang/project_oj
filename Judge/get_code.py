#!/usr/bin/env python
# coding=utf-8
import codecs
import logging
import os

import config
# from Judge.main import low_level


def get_code(id, question_id, language, code):
    """从数据库获取代码并写入work目录下对应的文件"""
    file_name = {
        "gcc": "main.c",
        "g++": "main.cpp",
        "java": "Main.java",
        'ruby': "main.rb",
        "perl": "main.pl",
        "pascal": "main.pas",
        "go": "main.go",
        "lua": "main.lua",
        'python2': 'main.py',
        'python3': 'main.py',
        "haskell": "main.hs"
    }
    try:
        work_path = os.path.join(config.work_dir, str(id))
        # low_level()
        os.mkdir(work_path)
    except OSError as e:
        if str(e).find("exist") > 0:  # 文件夹已经存在
            pass
        else:
            logging.error(e)
            return False
    try:
        real_path = os.path.join(
            config.work_dir,
            str(id),
            file_name[language])
    except KeyError as e:
        logging.error(e)
        return False
    try:
        # low_level()
        f = codecs.open(real_path, 'w')
        try:
            # print(real_path)
            f.write(code)
        except:
            logging.error("%s not write code to file" % id)
            f.close()
            return False
        f.close()
    except OSError as e:
        logging.error(e)
        return False
    # print('success')
    return True

#
# if __name__ == '_ _main__':
#     get_code(1, 2, "java", "123142")
