# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from common.mymako import render_mako_context, render_json
from blueking.component.shortcuts import get_client_by_request
from doctest import script_from_examples
from conf.default import STATICFILES_DIRS
from home_application.models import RollLog
import os,base64,copy,datetime,re,json

def execute_rolllog(request,conf):
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
    client = get_client_by_request(request)
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
    #RollLog.objects.create(conf_id=conf.id, task_instance_id=task_instance_id, log_size=-1, scan_time=now,do_time=now,do_result=-1)
    return render_json({'result':True});

def execute_rolllog_conf(request):
    rolllog = RollLog.objects.all()
    if len(rolllog) == 0:
        return
    now = datetime.datetime.now()
    for conf in rolllog:
        if conf.scan_time is None:
            print "scan_time" 
        if (conf.scan_time is None) or ((now - conf.scan_time).seconds >= conf.roll_cron):
            execute_rolllog(request,conf)
        
    return render_json({'result':True}); 

#     target_ports = str(target_port).split(',')
#     for target_port in target_ports:
#         t = Thread(target = nmapScan,args = (str(host), str(target_ip), str(target_port)))
#         t.start()  

def get_script_logs(request):
    rolllog = RollLog.objects.filter(is_get_result=0)
    if len(rolllog) == 0:
        return
    client = get_client_by_request(request)
    for log in rolllog:        
        kwargs = {
            "task_instance_id": log.task_instance_id         
        }
        result = client.job.get_task_ip_log(kwargs);
        ipLogContent = result.get('data')[0].get('stepAnalyseResult')[0].get('ipLogContent')[0]
        exitCode = ipLogContent.get('exitCode')
        if exitCode == 255 or exitCode == 0:     
            startTime = datetime.datetime.strptime(ipLogContent.get('startTime') , "%Y-%m-%d %H:%M:%S") 
            logContent = ipLogContent.get('logContent') 
            logsize = re.findall("logsize=\d+", logContent)[0].split("=")[1];  
        RollLog.objects.filter(id=log.id).update(scan_log_size=logsize,do_result=exitCode,do_time=startTime,is_get_result=1)

    
    return render_json({'result':True});    

def save_rolllog(request):
    username = request.POST.get('username') 
    biz_id = request.POST.get('biz_id') 
    biz_name = request.POST.get('biz_name') 
    biz_ip = eval(request.POST.get('biz_ip')) 
    log_path = request.POST.get('log_path') 
    log_size = int(request.POST.get('log_size'))*1024*1024 #M 
    roll_cron = request.POST.get('roll_cron')
    roll_cron_detail = request.POST.get('roll_cron_detail')  
    ips = biz_ip.keys();
    ret_text = "保存成功";
    ret_code = True;
    try:
        for ip in ips:
            RollLog.objects.create(biz_id=biz_id,biz_name=biz_name,biz_ip=ip,biz_ip_source=biz_ip[ip],log_path=log_path,log_size=log_size,roll_cron=roll_cron,roll_cron_detail=roll_cron_detail,username=username)
    except:
        ret_code = False;
        ret_text = "保存异常"
    return render_json({'result':ret_code, 'text':ret_text});
   
'''
records = {
    app_id : {
        app_id:x
        app_name:x
        host_id:{
            InnerIP:Source
        }
    }    
}
'''
def get_user_ips(request):
    username = request.POST.get('username')  
    host_ip = {};   
    record = {};
    records = {};
    ret_text = "调用成功";
    ret_code = True;
    ret_num = 0;
    if username == "":
        return render_json({'result':False, 'ret_text':"未获取到用户信息"});
    try: 
        client = get_client_by_request(request)
        apps = client.cc.get_app_by_user(username)
        if apps.get('code') == 0:
            app_num = 0;
            for app in apps.get('data'):
                app_id = app.get('ApplicationID')
                app_name = app.get('ApplicationName')
                app_num += 1;
                kwargs = {
                    "app_id":app_id 
                }
                hosts = client.cc.get_app_host_list(kwargs)
                if hosts.get('code') == 0:
                    record["app_id"] = app_id;
                    record["app_name"] = app_name;
                    host_ip.clear();
                    for host in hosts.get('data'):
                        InnerIP = host.get('InnerIP')
                        Source = host.get('Source')
                        host_ip[InnerIP] = Source;   
                    ret_num += len(host_ip.keys());                 
                    record["host_ip"] = copy.deepcopy(host_ip);
                records[str(app_id)] = copy.deepcopy(record);
    except:
        ret_code = False;
        ret_text = "获取用户业务主机异常"
        
    if ret_num == 0:
        ret_code = False;
        ret_text = "没有查询到相关业务主机数据"
         
    return render_json({'result':ret_code, 'text':ret_text,  'renum':ret_num , 'records':records});

def get_user_biz(request):
    username = request.POST.get('username')  
    records = {};
    ret_text = "调用成功";
    ret_code = True;
    ret_num = 0;
    if username == "":
        return render_json({'result':False, 'ret_text':"未获取到用户信息"});
    try: 
        client = get_client_by_request(request)
        apps = client.cc.get_app_by_user(username)
        if apps.get('code') == 0:
            app_num = 0;
            for app in apps.get('data'):
                app_id = app.get('ApplicationID')
                app_name = app.get('ApplicationName')
                ret_num += 1; 
                records[str(app_id)] = app_name                
    except:
        ret_code = False;
        ret_text = "获取用户业务数据异常"
        
    if ret_num == 0:
        ret_code = False;
        ret_text = "没有查询到相关业务"
         
    return render_json({'result':ret_code, 'text':ret_text,  'renum':ret_num , 'records':records});

def get_roll_logs(request):
    username = request.POST.get('username')  
    biz_id = request.POST.get('biz_id')     
    biz_ip = request.POST.get('biz_ip') 
    file_name = request.POST.get('file_name') 
    ret_text = "查询成功";
    ret_code = True;
    ret_num = 0;
    if username == "":
        return render_json({'result':False, 'ret_text':"未获取到用户信息"});      
    try: 
        rolllog = RollLog.objects.all() 
        ret_num = len(rolllog);             
    except:
        ret_code = False;
        ret_text = "查询记录异常"
        
    if ret_num == 0:
        ret_code = False;
        ret_text = "没有查询到相关数据"
        
    logs = [];
    for log in rolllog:  
        logs.append({'id':log.id,'biz_name':log.biz_name,'biz_ip':log.biz_ip,'log_path':log.log_path,'log_size':log.log_size,'scan_time':str(log.scan_time),'scan_log_size':log.scan_log_size,'do_time':str(log.do_time),'do_result':log.do_result})  
    records = json.dumps(logs) 
         
    return render_json({'result':ret_code, 'text':ret_text,  'renum':ret_num , 'records':records});

def del_rolllog(request):
    id = request.POST.get('id')     
    ret_text = "删除成功";
    ret_code = True;   
    try: 
        RollLog.objects.filter(id=id).delete()             
    except:
        ret_code = False;
        ret_text = "删除记录异常"
         
    return render_json({'result':ret_code, 'text':ret_text});


def home(request):
    """
    日志管理查询页面
    """
    return render_mako_context(request, '/home_application/home.html')

def roll_log_conf(request):
    """
    日志管理配置页面
    """
    return render_mako_context(request, '/home_application/roll_log_conf.html')

