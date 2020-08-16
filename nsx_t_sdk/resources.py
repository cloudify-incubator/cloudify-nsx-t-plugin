########
# Copyright (c) 2020 Cloudify Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from nsx_t_sdk.common import NSXTResource


class LogicalSwitch(NSXTResource):
    client_type = 'nsx'
    resource_type = 'LogicalSwitch'
    service_name = 'LogicalSwitches'


class Segment(NSXTResource):
    client_type = 'nsx_infra'
    resource_type = 'Segment'
    service_name = 'Segments'


class SegmentState(NSXTResource):
    client_type = 'segment'
    resource_type = 'State'
    service_name = 'State'

    allow_create = False
    allow_delete = False
    allow_get = True
    allow_list = False
    allow_update = False
