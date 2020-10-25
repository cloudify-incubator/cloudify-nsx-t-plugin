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

from com.vmware.nsx_policy.model_client import \
    DhcpServerConfig as vmDhcpServerConfig

# Local Imports
from nsx_t_plugin.tests.base import NSXTPluginTestBase
from nsx_t_plugin.dhcp_server import dhcp_server_config


@mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client')
class DHCPServerConfigTestCase(NSXTPluginTestBase):

    @property
    def resource_config(self):
        config = {
            'id': 'test_dhcp_server',
            'display_name': 'Test DHCP Server',
            'description': 'Test DHCP Server Config',
            'edge_cluster_path': '/infra/sites/default/cluster-path',
            'tags': [
                {
                    'scope': 'Name',
                    'tag': 'Test DHCP'
                }
            ]
        }
        return config

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    @mock.patch('nsx_t_sdk.resources.DhcpServerConfig.create')
    def test_create_dhcp_server_config(self, mock_create, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.create')
        res = copy.deepcopy(self.resource_config)
        res['path'] = '/test/path/dhcp-server-config'
        mock_create.return_value = vmDhcpServerConfig(**res)
        mock_invoke.return_value = vmDhcpServerConfig(**res)
        dhcp_server_config.create()

        self.assertEqual(
            self._ctx.instance.runtime_properties['id'],
            'test_dhcp_server'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['name'],
            'Test DHCP Server'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['type'],
            dhcp_server_config.DhcpServerConfig.resource_type
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['path'],
            '/test/path/dhcp-server-config'
        )

    @mock.patch('nsx_t_plugin.dhcp_server.dhcp_server_config'
                '._update_tier_1_gateway')
    def test_configure_dhcp_server_config(self,
                                          mock_update_tier1_gateway,
                                          _):
        node_properties = {}
        node_properties['tier1_gateway_id'] = 'test_tier1_gateway_id'
        node_properties.update(self.node_properties)
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=node_properties,
            test_runtime_properties={
                'id': 'test_dhcp_server',
                'name': 'Test DHCP Server',
                'type': dhcp_server_config.DhcpServerConfig.resource_type,
                'path': '/test/path/dhcp-server-config'
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.configure')

        dhcp_server_config.configure()
        mock_update_tier1_gateway.assert_called_with(
            self.client_config,
            'test_tier1_gateway_id',
            ['/test/path/dhcp-server-config']
        )

    @mock.patch('nsx_t_plugin.dhcp_server.dhcp_server_config'
                '._update_tier_1_gateway')
    def test_stop_configure_dhcp_server_config(self,
                                               mock_update_tier1_gateway,
                                               _):
        node_properties = {}
        node_properties['tier1_gateway_id'] = 'test_tier1_gateway_id'
        node_properties.update(self.node_properties)
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=node_properties,
            test_runtime_properties={
                'id': 'test_dhcp_server',
                'name': 'Test DHCP Server',
                'type': dhcp_server_config.DhcpServerConfig.resource_type,
                'path': '/test/path/dhcp-server-config'
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.stop')
        dhcp_server_config.stop()
        mock_update_tier1_gateway.assert_called_with(
            self.client_config,
            'test_tier1_gateway_id',
            []
        )

    @mock.patch('nsx_t_sdk.resources.DhcpServerConfig.delete')
    def test_delete_dhcp_server_config(self, mock_delete, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={
                'id': 'test_dhcp_server',
                'name': 'Test DHCP Server',
                'type': dhcp_server_config.DhcpServerConfig.resource_type,
                'path': '/test/path/dhcp-server-config'
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')

        dhcp_server_config.delete()

        self.assertTrue(
            'id' not in self._ctx.instance.runtime_properties
        )
        self.assertTrue(
            'name' not in self._ctx.instance.runtime_properties
        )
        self.assertTrue(
            'type' not in self._ctx.instance.runtime_properties
        )
        self.assertTrue(
            'path' not in self._ctx.instance.runtime_properties
        )
        mock_delete.assert_called()
