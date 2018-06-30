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

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home'),
    (r'^roll_log_conf/$', 'roll_log_conf'),
    (r'^get_user_ips/$', 'get_user_ips'), 
    (r'^get_user_biz/$', 'get_user_biz'),    
    (r'^get_roll_logs/$', 'get_roll_logs'),  
    (r'^get_script_logs/$', 'get_script_logs'),  
    (r'^save_rolllog/$', 'save_rolllog'),  
    (r'^del_rolllog/$', 'del_rolllog'),      
    (r'^execute_rolllog_conf/$', 'execute_rolllog_conf'),                 
)
