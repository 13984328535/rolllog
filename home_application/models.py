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

class RollLog(models.Model):
    biz_id = models.IntegerField(u"业务ID")
    biz_name = models.CharField(u"业务名称", max_length=255)
    biz_ip = models.CharField(u"业务主机", max_length=20)
    biz_ip_source = models.IntegerField(u"主机SOURCE")
    log_path = models.CharField(u"文件路径", max_length=1024)
    log_size = models.BigIntegerField(u"文件大小")
    roll_cron = models.IntegerField(u"检查周期")
    roll_cron_detail = models.CharField(u"周期说明", max_length=20)
    username = models.CharField(u"用户名", max_length=40)
    scan_time = models.DateTimeField(u"最后检查时间", null=True, blank=True)
    scan_log_size = models.BigIntegerField(u"检查时文件大小", default=-1)
    do_time = models.DateTimeField(u"最后处理日志时间", null=True, blank=True)
    do_result = models.IntegerField(u"处理结果", default=-1)
    is_get_result = models.IntegerField(u"是否获取结果", default=1)
    task_instance_id = models.BigIntegerField(u"最后任务实例ID", null=True, blank=True)

    
    