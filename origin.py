import logging
import time
import pymysql

from multiprocessing import Manager, Pool
import subprocess

from pymysql import OperationalError


def run_sql(sql):
    """执行sql语句,并返回结果"""
    con = None
    while True:
        try:
            con = pymysql.connect(host='localhost', port=3306, user='root', password='1059291245',
                                  db='oj', charset='utf8')
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


def producer(q, lock):
    """循环扫描数据库,将任务添加到队列"""
    while True:
        if q.full():
            q.join()
        sql = "#####"
        lock.acquire()
        data = run_sql('select * from submission where message is NULL')
        lock.release()
        for i in data:
            id, user_id, question_id, content, language, message = i
            task = {
                "id": id,
                "user_id": user_id,
                "question_id": question_id,
                "content": content,
                "language": language,
            }
            q.put(task)
        time.sleep(0.5)


def worker(q, lock):
    """工作进程，循环扫描队列，获得评判任务并执行"""
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
        compile()
        # result=run()
        lock.acquire()
        # 将结果写入数据库
        lock.release()
        q.task_done()


def start_work():
    """开启工作进程"""
    q = Manager().Queue(10)
    lock = Manager().Lock()
    size = 4
    pool = Pool(processes=size)
    pool.apply_async(func=producer, args=(q, lock))
    for i in range(size - 1):
        pool.apply_async(func=worker, args=(q, lock))
    pool.close()
    pool.join()


def compile(solution_id,language):
    '''将程序编译成可执行文件'''
    build_cmd = {
        "gcc"    : "gcc main.c -o main -Wall -lm -O2 -std=c99 --static -DONLINE_JUDGE",
        "g++"    : "g++ main.cpp -O2 -Wall -lm --static -DONLINE_JUDGE -o main",
        "java"   : "javac Main.java",
        "ruby"   : "ruby -c main.rb",
        "perl"   : "perl -c main.pl",
        "pascal" : 'fpc main.pas -O2 -Co -Ct -Ci',
        "go"     : '/opt/golang/bin/go build -ldflags "-s -w"  main.go',
        "lua"    : 'luac -o main main.lua',
        "python2": 'python2 -m py_compile main.py',
        "python3": 'python3 -m py_compile main.py',
        "haskell": "ghc -o main main.hs",
    }
    p = subprocess.Popen(build_cmd[language],shell=True,cwd=dir_work,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err =  p.communicate()#获取编译错误信息
    if p.returncode == 0: #返回值为0,编译成功
        return True
    dblock.acquire()
    update_compile_info(solution_id,err+out) #编译失败,更新题目的编译错误信息
    dblock.release()
    return False

#
# def judge_result(problem_id,solution_id,data_num):
#     '''对输出数据进行评测'''
#     currect_result = os.path.join(config.data_dir,str(problem_id),'data%s.out'%data_num)
#     user_result = os.path.join(config.work_dir,str(solution_id),'out%s.txt'%data_num)
#     try:
#         curr = file(currect_result).read().replace('\r', '').rstrip()#删除\r,删除行末的空格和换行
#         user = file(user_result).read().replace('\r', '').rstrip()
#     except:
#         return False
#     if curr == user:       #完全相同:AC
#         return "Accepted"
#     if curr.split() == user.split(): #除去空格,tab,换行相同:PE
#         return "Presentation Error"
#     if curr in user:  #输出多了
#         return "Output limit"
#     return "Wrong Answer"  #其他WA


# def get_max_mem(pid):
#     '''获取进程号为pid的程序的最大内存'''
#     glan = psutil.Process(pid)
#     max = 0
#     while True:
#         try:
#             rss,vms = glan.get_memory_info()
#             if rss > max:
#                 max = rss
#         except:
#             print "max rss = %s"%max
#             return max
#
#

#
# def run(problem_id,solution_id,language,data_count,user_id):
#     '''获取程序执行时间和内存'''
#     time_limit = (time_limit+10)/1000.0
#     mem_limit = mem_limit * 1024
#     max_rss = 0
#     max_vms = 0
#     total_time = 0
#     for i in range(data_count):
#         '''依次测试各组测试数据'''
#         args = shlex.split(cmd)
#         p = subprocess.Popen(args,env={"PATH":"/nonexistent"},cwd=work_dir,stdout=output_data,stdin=input_data,stderr=run_err_data)
#         start = time.time()
#         pid = p.pid
#         glan = psutil.Process(pid)
#         while True:
#             time_to_now = time.time()-start + total_time
#             if psutil.pid_exists(pid) is False:
#                 program_info['take_time'] = time_to_now*1000
#                 program_info['take_memory'] = max_rss/1024.0
#                 program_info['result'] = result_code["Runtime Error"]
#                 return program_info
#             rss,vms = glan.get_memory_info()
#             if p.poll() == 0:
#                 end = time.time()
#                 break
#             if max_rss < rss:
#                 max_rss = rss
#                 print 'max_rss=%s'%max_rss
#             if max_vms < vms:
#                 max_vms = vms
#             if time_to_now > time_limit:
#                 program_info['take_time'] = time_to_now*1000
#                 program_info['take_memory'] = max_rss/1024.0
#                 program_info['result'] = result_code["Time Limit Exceeded"]
#                 glan.terminate()
#                 return program_info
#             if max_rss > mem_limit:
#                 program_info['take_time'] = time_to_now*1000
#                 program_info['take_memory'] = max_rss/1024.0
#                 program_info['result'] =result_code["Memory Limit Exceeded"]
#                 glan.terminate()
#                 return program_info
#
#         logging.debug("max_rss = %s"%max_rss)
# #        print "max_rss=",max_rss
#         logging.debug("max_vms = %s"%max_vms)
# #        logging.debug("take time = %s"%(end - start))
#     program_info['take_time'] = total_time*1000
#     program_info['take_memory'] = max_rss/1024.0
#     program_info['result'] = result_code[program_info['result']]
#     return program_info
