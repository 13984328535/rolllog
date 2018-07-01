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
from blueking.component.shortcuts import get_client_by_request,get_client_by_user
from doctest import script_from_examples
from conf.default import STATICFILES_DIRS
from home_application.models import RollLog
import os,base64,copy,datetime,re,json

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
                        osType = host.get('osType')
                        if osType == "linux":
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
        if biz_id == "0":
            if biz_ip == "" and file_name == "":
                rolllog = RollLog.objects.all() 
            if biz_ip != "" and file_name == "":
                rolllog = RollLog.objects.filter(biz_ip=biz_ip)
            if biz_ip == "" and file_name != "":
                rolllog = RollLog.objects.filter(log_path__contains=file_name)
            if biz_ip != "" and file_name != "":
                rolllog = RollLog.objects.filter(biz_ip=biz_ip,log_path__contains=file_name)                
        else:  
            if biz_ip == "" and file_name == "":
                rolllog = RollLog.objects.filter(biz_id=biz_id)
            if biz_ip != "" and file_name == "":
                rolllog = RollLog.objects.filter(biz_id=biz_id,biz_ip=biz_ip)
            if biz_ip == "" and file_name != "":
                rolllog = RollLog.objects.filter(biz_id=biz_id,log_path__contains=file_name)  
            if biz_ip != "" and file_name != "":
                rolllog = RollLog.objects.filter(biz_id=biz_id,biz_ip=biz_ip,log_path__contains=file_name)                               
                
        ret_num = len(rolllog);             
    except:
        ret_code = False;
        ret_text = "查询记录异常"
        
    if ret_num == 0:
        ret_code = False;
        ret_text = "没有查询到相关数据"
        
    logs = [];
    for log in rolllog:  
        logs.append({'id':log.id,'biz_name':log.biz_name,'biz_ip':log.biz_ip,'log_path':log.log_path,'log_size':log.log_size,'roll_cron_detail':log.roll_cron_detail, 'scan_time':str(log.scan_time),'scan_log_size':log.scan_log_size,'scan_result':log.scan_result,'do_time':str(log.do_time),'do_result':log.do_result})  
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

