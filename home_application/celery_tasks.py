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
from blueking.component.shortcuts import get_client_by_user
from conf.default import STATICFILES_DIRS
from home_application.models import RollLog
import os,base64,copy,re,json

@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week="*"))
def execute_rolllog_logs():
    """
    celery 周期任务
    """
    execute_task()
    now = datetime.datetime.now()
    logger.error(u"celery execute_rolllog_logs 周期任务调用开始，当前时间：{}".format(now)) 
    rolllog = RollLog.objects.filter(is_get_result=0)
    if len(rolllog) == 0:
        return    
    for log in rolllog:  
        client = get_client_by_user(log.username)      
        kwargs = {
            "task_instance_id": log.task_instance_id         
        }
        result = client.job.get_task_ip_log(kwargs);
        ipLogContent = result.get('data')[0].get('stepAnalyseResult')[0].get('ipLogContent')[0]
        exitCode = ipLogContent.get('exitCode')
        if exitCode == 255 or exitCode == 0:     
            #startTime = datetime.datetime.strptime(ipLogContent.get('startTime') , "%Y-%m-%dT%H:%M:%S") 
            now = datetime.datetime.now()
            logContent = ipLogContent.get('logContent') 
            logger.error(u"logContent="+logContent) 
            logsize = re.findall("logsize=\d+", logContent)[0].split("=")[1];  
            RollLog.objects.filter(id=log.id).update(scan_log_size=logsize,do_result=exitCode,do_time=now,is_get_result=1)
        elif exitCode == 3:
            RollLog.objects.filter(id=log.id).update(do_result=exitCode,is_get_result=1)

@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week="*"))
def execute_rolllog_conf():
    """
    celery 周期任务
    """
    execute_task()
    now = datetime.datetime.now()
    logger.error(u"celery execute_rolllog_conf 周期任务调用开始，当前时间：{}".format(now)) 
    rolllog = RollLog.objects.all()
    if len(rolllog) == 0:
        return
    now = datetime.datetime.now()
    for conf in rolllog:
        if (conf.scan_time is None) or ((now - conf.scan_time).seconds >= conf.roll_cron):
            execute_rolllog(conf)

def execute_rolllog(conf):
    staticdir = ','.join(STATICFILES_DIRS);
    script_path = os.path.join(staticdir, str('script'))
    file = os.path.join(script_path, 'roll_log.sh')
    with open(file) as f:
        script_content = f.read()
    f.close()
    
    biz_ips = {}
    biz_ips["ip"] = conf.biz_ip;
    biz_ips["source"] = conf.biz_ip_source;
    ip_list = [];
    ip_list.append(biz_ips);
    param = '%s %s' % (conf.log_path, conf.log_size)
    client = get_client_by_user(conf.username)
    kwargs = {
        "username":conf.username, 
        "app_id":conf.biz_id,
        "content":base64.encodestring(script_content),
        "script_param":param,
        "ip_list":ip_list, "type":1, "account":'root',            
    }
    result = client.job.fast_execute_script(kwargs);
    if result['code'] != 0:
        return render_json({'result':False});
    task_instance_id = result['data']['taskInstanceId']
    now = datetime.datetime.now()
    RollLog.objects.filter(id=conf.id).update(scan_time=now,task_instance_id=task_instance_id,is_get_result=0)
        

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
    
        
