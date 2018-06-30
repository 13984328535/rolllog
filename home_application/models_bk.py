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

from django.db import models

class MultRecode(models.Model):
    multiplier = models.IntegerField(u"乘数")
    multiplicand = models.IntegerField(u"被乘数")
    mult_result = models.IntegerField(u"结果")
     
class PortScan(models.Model):
    source_hostname = models.CharField(u"源主机名", max_length=80)
    target_ip = models.CharField(u"目标IP",max_length=1024)
    target_port = models.CharField(u"目标端口",max_length=1024)
    state = models.CharField(u"状态",max_length=20)
    protocol = models.CharField(u"协议",max_length=10)   
    scan_time = models.DateTimeField(u"扫描时间", auto_now=True)
    
class PortScanPara(models.Model):
    source_hostname = models.CharField(u"源主机名", max_length=80)
    target_ip = models.CharField(u"目标IP",max_length=1024)
    target_port = models.CharField(u"目标端口",max_length=1024)
    protocol = models.CharField(u"协议",max_length=10)   
    oper_time = models.DateTimeField(u"扫描时间", auto_now=True)
    opere_hostname = models.CharField(u"执行主机", max_length=80)
       
    
    
     
