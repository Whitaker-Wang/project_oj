#!/usr/bin/env python
# coding=utf-8
import shutil

import os

import config


def clean_work_dir(id):
    """清理目录，删除临时文件"""
    dir_name = os.path.join(config.work_dir, str(id))
    shutil.rmtree(dir_name)
