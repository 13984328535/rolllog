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
#from django.http import JsonResponse   同render_json
from home_application.models import MultRecode, PortScan, PortScanPara
from home_application.celery_tasks import async_portscan
import os  
import time
import json
import nmap
import re
import socket
from threading import Thread


def get_scan_records(request):
    all_record = PortScan.objects.all().order_by('id','target_ip','target_port')
    #all_record = PortScan.objects.filter(scan_time__gt=nowTime).order_by('scan_time')
    all_end = PortScan.objects.filter(state="正在扫描...").count()
    is_end = False;
    if all_end == 0:
        is_end = True
    records = []  
    for record in all_record:  
        records.append({'source_hostname':record.source_hostname,'target_ip':record.target_ip,'target_port':record.target_port,'state':record.state,'protocol':record.protocol,'scan_time':str(record.scan_time)})  
    scan_records = json.dumps(records) 
    return render_json({'result':True, 'all_record':scan_records, 'is_end':is_end})

    

def get_api(api_url, token):
    url = "%s%s" % (settings.BK_PAAS_HOST, api_url)
    textmod ={'bk_app_code':settings.APP_ID,
    'bk_app_secret':settings.APP_TOKEN,
    'bk_token':token }
    textmod = urllib.urlencode(textmod)

    req = urllib2.Request(url = '%s%s%s' % (url, '?', textmod))
    res = urllib2.urlopen(req)
    res = res.read()
    return res;

def hosttime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

def hostname():
    #hostname = socket.gethostname()
    #print hostname    
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
    
def hostIpList():  
    return socket.gethostbyname_ex(socket.gethostname())[2]   

def check_ip(ipAddr):
    compile_ip=re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ipAddr):
        return True 
    else:  
        return False

def nmapScan(hostname,tip, port):
    portscan_recode = PortScan(source_hostname=hostname, target_ip=tip, target_port=port,state="正在扫描...",protocol="TCP")
    portscan_recode.save()
    nmScan = nmap.PortScanner()
    nmScan.scan(tip, port)
    state = nmScan[tip]['tcp'][int(port)]['state']
    PortScan.objects.filter(source_hostname=hostname, target_ip=tip, target_port=port).update(state=state, scan_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))
    
def portScanCancel(request):
    PortScan.objects.filter().delete();
    PortScanPara.objects.filter().delete();
    return render_json({'result':True})
        
def portScan(request):
    #source_hostname = request.POST.get('source_hostname')
    target_ip = request.POST.get('target_ip')
    target_port = request.POST.get('target_port')
    host = hostname()
       
    if(target_ip == "" or target_port == ""):
        return render_json({'result':False, 'text':"参数不能为空"})
    
    ips = str(target_ip).split(',')
    for ip in ips: 
        if(check_ip(ip) == False):
            return render_json({'result':False, 'text':"请输入正确的目标IP"})
        
    ports = str(target_port).split(',')
    for port in ports: 
        if(port.isdigit() == False):
            return render_json({'result':False, 'text':"请输入正确的目标端口"})        
      
    PortScan.objects.filter().delete();
    PortScanPara.objects.filter().delete();
    PortScanPara.objects.create(source_hostname=host,target_ip=target_ip,target_port=target_port,protocol="TCP",opere_hostname="")
      
    async_portscan.delay();
    return render_json({'result':True})

def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')
