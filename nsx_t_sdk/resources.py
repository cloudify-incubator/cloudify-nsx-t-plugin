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

from nsx_t_sdk.common import (
    NSXTResource,
    ACTION_GET,
    ACTION_LIST
)
from nsx_t_sdk.exceptions import NSXTSDKException


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


class VirtualMachine(NSXTResource):
    client_type = 'fabric'
    resource_type = 'VirtualMachine'
    service_name = 'VirtualMachines'

    allow_create = False
    allow_delete = True
    allow_get = True
    allow_list = True
    allow_update = False
    allow_patch = False

    def get(self):
        self._validate_allowed_method(self.allow_get, ACTION_GET)
        display_name = self.resource_config.get('vm_name')
        external_id = self.resource_config.get('vm_id')
        if not any([display_name, external_id]):
            raise NSXTSDKException(
                'At least one virtual machine field '
                '`vm_name or vm_id` must '
                'be provided to lookup the vm resource'
            )
        results = self.list(
            filters={
                'display_name': display_name, 'external_id': external_id
            },
        )
        error_message = ''
        if not results:
            error_message = 'No virtual machine {0} found'.format(
                display_name or external_id
            )
        elif len(results) > 1:
            error_message = 'More than one virtual machine {0} found'.format(
                display_name or external_id
            )

        if error_message:
            raise NSXTSDKException(error_message)

        self.resource_id = results[0]['external_id']
        return results[0]


class VirtualNetworkInterface(NSXTResource):
    client_type = 'fabric'
    resource_type = 'VirtualNetworkInterface'
    service_name = 'Vifs'

    allow_create = False
    allow_delete = True
    allow_get = False
    allow_list = True
    allow_update = False
    allow_patch = False

    def list(self,
             cursor=None,
             included_fields=None,
             page_size=None,
             sort_ascending=None,
             sort_by=None,
             filters=None
             ):
        self._validate_allowed_method(self.allow_list, ACTION_LIST)
        results = super(VirtualNetworkInterface, self).list(filters=filters)
        return results
