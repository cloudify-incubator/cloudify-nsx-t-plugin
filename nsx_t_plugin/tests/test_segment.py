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

# Standard Imports
import copy

# Third Parties Imports
import mock

from com.vmware.nsx_policy.model_client import Segment as vmSegment

# Local Imports
from nsx_t_plugin.tests.base import NSXTPluginTestBase
from nsx_t_plugin.segment import segment


@mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client')
class SegmentTestCase(NSXTPluginTestBase):

    @property
    def resource_config(self):
        config = {
            'id': 'test_segment',
            'display_name': 'Test Segment',
            'description': 'Test Segment Config',
            'transport_zone_path': '/infra/test/default/transport-zone-path',
            'connectivity_path': '/infra/test/default/connectivity-path',
            'dhcp_config_path': '/infra/test/default/dhcp-config-path',
            'subnet': {
                'ip_v4_config': {
                    'dhcp_config': {
                        'server_address': '192.168.11.11/24',
                        'lease_time': '86400',
                        'resource_type': 'SegmentDhcpV4Config'
                    },
                    'gateway_address': '192.168.11.12/24',
                    'dhcp_ranges': ['192.168.11.100-192.168.11.160']

                },
                'ip_v6_config': {
                    'dhcp_config': {
                        'server_address': 'fc7e:f206:db42::6/48',
                        'lease_time': '86400',
                        'resource_type': 'SegmentDhcpV6Config'
                    },
                    'gateway_address': 'fc7e:f206:db42::2/48',
                    'dhcp_ranges': ['fc7e:f206:db42::15-fc7e:f206:db42::200']
                    }
                }
            }
        return config

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    @mock.patch('nsx_t_sdk.resources.Segment.create')
    def test_create_segment(self, mock_create, mock_invoke, _):
        # Test create operation with decorator
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        res = copy.deepcopy(self.resource_config)
        res['unique_id'] = 'unique_test_segment'
        segment._update_subnet_configuration(res)
        mock_create.return_value = vmSegment(**res)
        mock_invoke.return_value = vmSegment(**res)
        segment.create()

        self.assertEqual(
            self._ctx.instance.runtime_properties['unique_id'],
            'unique_test_segment'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['id'],
            'test_segment'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['name'],
            'Test Segment'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['type'],
            segment.Segment.resource_type
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['resource_config'],
            res
        )
