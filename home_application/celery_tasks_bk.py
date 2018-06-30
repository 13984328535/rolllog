# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import datetime

from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from common.log import logger
import os
import time
import re
import socket
from home_application.models import PortScanPara,PortScan
from threading import Thread
import nmap
    
def hostIpList():  
    return socket.gethostbyname_ex(socket.gethostname())[2]  
    
def check_ip(ipAddr):
    compile_ip=re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ipAddr):
        return True 
    else:  
        return False
        
def hostname():  
    sys = os.name  
    if sys == 'nt':  
        hostname = os.getenv('computername')  
        return hostname  
    elif sys == 'posix':  
        host = os.popen('echo $HOSTNAME')  
        try:  
            hostname = host.read()  
            return hostname  
        finally:  
            host.close()  
    else:  
        return 'Unkwon hostname'  
    
def nmapScan(hostname,tip, port):
    portscan_recode = PortScan(source_hostname=hostname, target_ip=tip, target_port=port,state="正在扫描...",protocol="TCP")
    portscan_recode.save()
    nmScan = nmap.PortScanner()
    nmScan.scan(tip, port, arguments='-T4 -Pn')
    state = nmScan[tip]['tcp'][int(port)]['state']
    PortScan.objects.filter(source_hostname=hostname, target_ip=tip, target_port=port).update(state=state, scan_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))

@task()
def async_portscan():
    logger.error(u"celery 定时任务执行成功，async_portscan")
    last_scantask = PortScanPara.objects.filter().last()
    host = hostname(); 
    
    source_hostname = last_scantask.source_hostname
    target_ip = last_scantask.target_ip
    target_port = last_scantask.target_port
    
    target_ips = str(target_ip).split(',')
    target_ports = str(target_port).split(',')
    for target_ip in target_ips: 
        for target_port in target_ports: 
            t = Thread(target = nmapScan,args = (str(source_hostname), str(target_ip), str(target_port)))
            t.start()             

@task()
def async_task(x, y):
    """
    定义一个 celery 异步任务
    """
    logger.error(u"celery 定时任务执行成功，执行结果：{:0>2}:{:0>2}".format(x, y))
    return x + y


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    now = datetime.datetime.now()
    logger.error(u"celery 定时任务启动，将在60s后执行，当前时间：{}".format(now))
    # 调用定时任务
    async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))


@periodic_task(run_every=crontab(minute='*/5', hour='*', day_of_week="*"))
def get_time():
    """
    celery 周期任务示例

    run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
    periodic_task：程序运行时自动触发周期任务
    """
    execute_task()
    now = datetime.datetime.now()
    logger.error(u"celery 周期任务调用成功，当前时间：{}".format(now))
    