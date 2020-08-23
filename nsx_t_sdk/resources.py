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


class State(NSXTResource):
    service_name = 'State'
    state_attr = 'state'
    allow_create = False
    allow_delete = False
    allow_get = True
    allow_list = False
    allow_update = False
    allow_patch = False


class Segment(NSXTResource):
    client_type = 'nsx_infra'
    resource_type = 'Segment'
    service_name = 'Segments'


class SegmentPort(NSXTResource):
    client_type = 'segment'
    resource_type = 'Port'
    service_name = 'Ports'

    allow_create = False
    allow_delete = True
    allow_get = True
    allow_list = True
    allow_update = False
    allow_patch = False


class SegmentState(State):
    client_type = 'segment'
    resource_type = 'SegmentState'


class DhcpServerConfig(NSXTResource):
    client_type = 'nsx_infra'
    resource_type = 'DhcpServerConfig'
    service_name = 'DhcpServerConfigs'


class Tier1(NSXTResource):
    client_type = 'nsx_infra'
    resource_type = 'Tier1'
    service_name = 'Tier1s'


class Tier1state(State):
    client_type = 'tier_1'
    resource_type = 'Tier1State'
    state_attr = 'tier1_state'
