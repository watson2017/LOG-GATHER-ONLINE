# - * - coding: utf-8 - * -

# 配置信息定义
# 执行步骤
#   1. 检查临时目录是否存在，检查旧版本包如果不存在就创建
#   2. 将对应服务器上的日志拷贝到java2上的临时目录
#   3. 根据情况判断是否进行压缩拷贝到内网服务器


# import conf
import datetime
import sys
import os
import sh
from sh import cd

TEMP_DIR = '/tmp'
Date = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
Logdata = datetime.datetime.now().strftime('%Y-%m-%d')
scp_cmd = sh.Command("/usr/bin/scp")
remote_log_path = ''
local_path = ''
logname = ''
logname1 = ''
logname2 = ''


def Check_args(hostname, program):
    u'''检测参数格式是否正确'''

    global remote_log_path, logname, logname1, logname2
    if hostname != 'java1' and hostname != 'java2' and hostname != 'java3' and hostname != 'java4' :
        print('''Please input right hostname,Include 'java1','java2','java3' or 'java4' in command ''')
        sys.exit(1)

    if (hostname == 'java1' or hostname == 'java2') and program != 'play':
        print("please check the relationship of hostname with program")
        sys.exit(1)
    elif (hostname == 'java3' or hostname == 'java4') and program != 'spring':
        print("please check the relationship of hostname with program")        
        sys.exit(1)

    if program == 'spring':
        remote_log_path = "/data/tomcat/logs"
        logname1 = "service.log"
        logname2 = "query.log"
    elif program == 'play':
        remote_log_path = "/data/tomcat/logs"
        logname = 'catalina_%s.%s.out' % (hostname, Logdata)
    else:
        print('''Please input right program name,For example 'play' or 'spring' in command ''')
        sys.exit(1)


def Spring_program(hostname, program):
    u'''spring 项目日志文件复制'''
    if program == 'spring':
        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname1), "%s/%s_%s_%s" % (local_path, Date, hostname, logname1))
        if output.exit_code:
            print("cp %s from remote failed." % (logname1))
        else:
            print("cp %s from remote succeed." % (logname1))

        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname2), "%s/%s_%s_%s" % (local_path, Date, hostname, logname2)) 
        if output.exit_code:
            print("cp %s from remote failed" % (logname2))
            sys.exit(1)
        else:
            print("cp %s from remote succeed. " % (logname2))      


def Play_program(hostname, program):
    u'''play 项目日志文件复制'''
    if program == 'play':
        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname), "%s/%s_%s" % (local_path, Date, logname))
        if output.exit_code:
            print("cp %s from remote failed." % (logname))
        else:
            print("cp %s from remote succeed." % (logname))


def CpLogTask(hostname, program):
    u'''复制日志文件到java2'''

    global local_path
    local_path = "%s/%s/%s" % (TEMP_DIR, hostname, program)
    Check_args(hostname, program)
    if os.path.exists(local_path) is not True:
        os.makedirs(local_path)
    print("mkdir local log path succeed.")   
    # 执行复制命令
    if program == 'spring':
        Spring_program(hostname, program)
    elif program == 'play':
        Play_program(hostname, program)
                       
    output = os.system("/usr/bin/sudo /bin/chown  tomcat.tomcat %s/* " % (local_path))
    if output is True:
        print("change privileges to tomcat failed.")
    else:
        print("change privileges to tomcat succeed.")


def CleanOld_log(hostname, program):
    u'''清理java2上旧日志'''

    Check_args(hostname, program)
    local_path = "%s/%s/%s" % (TEMP_DIR, hostname, program)
    for filename in os.listdir(local_path):
        if filename.endswith('.log') or filename.endswith('.out'):
            path_filename = os.path.join(local_path, filename)
            os.unlink(path_filename)
            print("clean old log %s succeed." % (filename))


def PackLog(hostname, program):
    u'''在java2上打包日志文件'''
    CpLogTask(hostname, program)
    local_path = "%s/%s" % (TEMP_DIR, hostname)
    cd(local_path)
    pack_name = "%s_%s.tar.gz" % (Date, program)
    tar_cmd = sh.Command("/bin/tar")
    output = tar_cmd("czf", "%s" % (pack_name), "%s" % (program))
    if output.exit_code:
        print("Compress log failed.")
    else:
        print("Compress log succeed.")


def all_play_spring():
    u'''复制所有的Spring以及play到java2上'''

    global remote_log_path
    global logname1, logname2, logname
    local_path = "/tmp/all_play_spring/play_spring"
    remote_log_path = "/data/tomcat/logs"
    logname1 = "service.log"
    logname2 = "query.log"

    if os.path.exists(local_path) is not True:
        os.makedirs(local_path)
    print("mkdir local log path succeed.")

    # 执行play复制命令
    for hostname in ('java1', 'java2'):
        logname = 'catalina_%s.%s.out' % (hostname, Logdata)
        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname), "%s/%s_%s" % (local_path, Date, logname))
        if output.exit_code:
            print("cp %s from remote failed." % (logname))
        else:
            print("cp %s from remote succeed." % (logname))

    # 执行Spring复制命令
    for hostname in ('java3', 'java4'):
        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname1), "%s/%s_%s_%s" % (local_path, Date, hostname, logname1))
        if output.exit_code:
            print("cp %s from remote failed." % (logname1))
        else:
            print("cp %s from remote succeed." % (logname1))

        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname2), "%s/%s_%s_%s" % (local_path, Date, hostname, logname2)) 
        if output.exit_code:
            print("cp %s from remote failed" % (logname2))
            sys.exit(1)
        else:
            print("cp %s from remote succeed. " % (logname2))


def allplay():
    u'''复制所有的play项目日志到java2'''
    global remote_log_path
    global logname
    local_path = "/tmp/allplay/play"
    remote_log_path = "/data/tomcat/logs"
    if os.path.exists(local_path) is not True:
        os.makedirs(local_path)
    print("mkdir local log path succeed.")   

    # 执行play复制命令
    for hostname in ('java1', 'java2'):
        logname = 'catalina_%s.%s.out' % (hostname, Logdata)
        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname), "%s/%s_%s" % (local_path, Date, logname))
        if output.exit_code:
            print("cp %s from remote failed." % (logname))
        else:
            print("cp %s from remote succeed." % (logname))

    output = os.system("/usr/bin/sudo /bin/chown  tomcat.tomcat %s/* " % (local_path))
    if output is True:
        print("change privileges to tomcat failed.")
    else:
        print("change privileges to tomcat succeed.")


def allspring():
    u'''复制所有的Spring项目日志到java2'''

    global remote_log_path
    global logname1, logname2
    local_path = "/tmp/allspring/spring"
    remote_log_path = "/data/tomcat/logs"
    logname1 = "service.log"
    logname2 = "query.log"

    if os.path.exists(local_path) is not True:
        os.makedirs(local_path)
    print("mkdir local log path succeed.")   

    # 执行复制命令
    for hostname in ('java3', 'java4'):
        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname1), "%s/%s_%s_%s" % (local_path, Date, hostname, logname1))
        if output.exit_code:
            print("cp %s from remote failed." % (logname1))
        else:
            print("cp %s from remote succeed." % (logname1))

        output = scp_cmd("-P22", "%s:%s/%s" % (hostname, remote_log_path, logname2), "%s/%s_%s_%s" % (local_path, Date, hostname, logname2)) 
        if output.exit_code:
            print("cp %s from remote failed" % (logname2))
            sys.exit(1)
        else:
            print("cp %s from remote succeed. " % (logname2))
        
    output = os.system("/usr/bin/sudo /bin/chown  tomcat.tomcat %s/* " % (local_path))
    if output is True:
        print("change privileges to tomcat failed.")
    else:
        print("change privileges to tomcat succeed.")


def pack_all_play_spring():
    u'''打包所有的Spring+play日志'''

    all_play_spring()
    local_path = "%s/%s" % (TEMP_DIR, 'all_play_spring')
    cd(local_path)
    pack_name = "%s_%s.tar.gz" % (Date, 'all_play_spring')
    tar_cmd = sh.Command("/bin/tar")
    output = tar_cmd("czf", "%s" % (pack_name), "%s" % ('play_spring'))
    if output.exit_code:
        print("Compress log failed.")
    else:
        print("Compress log succeed.")


def pack_allplay():
    u'''打包play项目'''
    allplay()
    local_path = "%s/%s" % (TEMP_DIR, 'allplay')
    cd(local_path)
    pack_name = "%s_%s.tar.gz" % (Date, 'play')
    tar_cmd = sh.Command("/bin/tar")
    output = tar_cmd("czf", "%s" % (pack_name), "%s" % ('play'))
    if output.exit_code:
        print("Compress log failed.")
    else:
        print("Compress log succeed.")
    

def pack_allspring():
    u'''打包所有的Spring项目日志'''

    allspring()
    local_path = "%s/%s" % (TEMP_DIR, 'allspring')
    cd(local_path)
    pack_name = "%s_%s.tar.gz" % (Date, 'spring')
    tar_cmd = sh.Command("/bin/tar")
    output = tar_cmd("czf", "%s" % (pack_name), "%s" % ('spring'))
    if output.exit_code:
        print("Compress log failed.")
    else:
        print("Compress log succeed.")


def CleanallSpringLog():
    local_path = "/tmp/allspring/spring"
    for filename in os.listdir(local_path):
        if filename.endswith('.log') or filename.endswith('.out'):
            path_filename = os.path.join(local_path, filename)
            os.unlink(path_filename)
            print("clean old log %s succeed." % (filename)) 


def CleanallPlayLog():
    local_path = "/tmp/allplay/play"
    for filename in os.listdir(local_path):
        if filename.endswith('.log') or filename.endswith('.out'):
            path_filename = os.path.join(local_path, filename)
            os.unlink(path_filename)
            print("clean old log %s succeed." % (filename))


def CleanlallSpringPlayLog():
    local_path = "/tmp/all_play_spring/play_spring"
    for filename in os.listdir(local_path):
        if filename.endswith('.log') or filename.endswith('.out'):
            path_filename = os.path.join(local_path, filename)
            os.unlink(path_filename)
            print("clean old log %s succeed." % (filename))   
                           