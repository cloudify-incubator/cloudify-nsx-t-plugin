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

from com.vmware.nsx_policy.model_client import (
    Segment as vmSegment,
    DhcpV4StaticBindingConfig as vmDhcpV4StaticBindingConfig,
    DhcpV6StaticBindingConfig as vmDhcpV6StaticBindingConfig,
    SegmentConfigurationState
)
from com.vmware.vapi.std.errors_client import Error, NotFound

from cloudify.exceptions import NonRecoverableError, OperationRetry

# Local Imports
from nsx_t_plugin.tests.base import (
    NSXTPluginTestBase,
    CustomMockContext,
    MockNodeInstanceContext,
    MockNodeContext
)
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

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_start_segment_on_success(self, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.start')
        mock_invoke.return_value = SegmentConfigurationState(
            state='success'
        )
        segment.start()

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_start_segment_on_pending(self, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.start')
        mock_invoke.return_value = SegmentConfigurationState(
            state='pending'
        )
        with self.assertRaises(OperationRetry):
            segment.start()

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_start_segment_on_failed(self, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.start')
        mock_invoke.return_value = SegmentConfigurationState(
            state='failed'
        )
        with self.assertRaises(NonRecoverableError):
            segment.start()

    @mock.patch('nsx_t_sdk.resources.DhcpV6StaticBindingConfig.list')
    @mock.patch('nsx_t_sdk.resources.DhcpV4StaticBindingConfig.list')
    def test_stop_segment_with_dhcp_resource(self,
                                             mock_dhcp4_list,
                                             mock_dhcp6_list,
                                             _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.stop')

        mock_dhcp4_list.return_value = [
            {
                'id': 'dhcpv4_1'
            },
            {
                'id': 'dhcpv4_2'
            },
        ]
        mock_dhcp6_list.return_value = [
            {
                'id': 'dhcpv6_1'
            },
            {
                'id': 'dhcpv6_2'
            },
        ]
        with self.assertRaises(OperationRetry):
            segment.stop()

    @mock.patch('nsx_t_sdk.resources.DhcpV6StaticBindingConfig.list')
    @mock.patch('nsx_t_sdk.resources.DhcpV4StaticBindingConfig.list')
    def test_stop_segment_with_no_dhcp_resource(self,
                                                mock_dhcp4_list,
                                                mock_dhcp6_list,
                                                _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.stop')

        mock_dhcp4_list.return_value = []
        mock_dhcp6_list.return_value = []
        segment.stop()

    @mock.patch('nsx_t_sdk.resources.Segment.delete')
    @mock.patch('nsx_t_sdk.resources.Segment.get')
    def test_delete_segment_in_progress(self,
                                        mock_get_segment,
                                        mock_delete_segment,
                                        _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_delete_segment.return_value = None
        mock_get_segment.return_value = vmSegment(id='test_segment')
        with self.assertRaises(OperationRetry):
            segment.delete()

    @mock.patch('nsx_t_sdk.resources.Segment.delete')
    @mock.patch('nsx_t_sdk.resources.Segment.get')
    def test_delete_segment_in_progress_with_error(self,
                                                   mock_get_segment,
                                                   mock_delete_segment,
                                                   _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_delete_segment.side_effect = Error
        mock_get_segment.return_value = vmSegment(id='test_segment')
        with self.assertRaises(OperationRetry):
            segment.delete()

    @mock.patch('nsx_t_sdk.resources.Segment.get')
    def test_delete_segment_in_progress_with_success(self,
                                                     mock_get_segment,
                                                     _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_segment'},
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_get_segment.side_effect = NotFound
        segment.delete()

    @mock.patch('nsx_t_sdk.resources.DhcpStaticBindingState.get')
    @mock.patch('nsx_t_sdk.resources.DhcpV6StaticBindingConfig.update')
    @mock.patch('nsx_t_sdk.resources.DhcpV4StaticBindingConfig.update')
    def test_add_static_bindings(self,
                                 mock_update_binding_v4,
                                 mock_update_binding_v6,
                                 mock_get_state_binding,
                                 _):
        target = CustomMockContext({
            'instance': MockNodeInstanceContext(
                id='test_segment_wjkog',
                runtime_properties={
                }),
            'node': MockNodeContext(
                id='test_segment',
                properties={
                    'client_config': self.client_config,
                    'resource_config': self.resource_config,
                }
            ), '_context': {
                'node_id': 'test_segment'
            }})

        source = CustomMockContext({
            'instance': MockNodeInstanceContext(
                id='vpshere_server_okijw',
                runtime_properties={
                    'networks': [
                        {
                            'name': 'test_nic1',
                            'mac': 'test_mac1'
                        },
                        {
                            'name': 'test_nic2',
                            'mac': 'test_mac2'
                        }

                    ],
                    'id': 'vpshere_server_loki'
                }),
            'node': MockNodeContext(
                id='vpshere_server_loki',
                properties={
                    'client_config': self.client_config,
                    'resource_config': self.resource_config,
                }
            ), '_context': {
                'node_id': 'vpshere_server'
            }})
        self._set_context_operation(
            instance_type='relationship-instance',
            source=source,
            target=target,
            ctx_operation_name='cloudify.interfaces.'
                               'relationship_lifecycle.preconfigure',
            node_id='test_segment'
        )

        mock_update_binding_v4.return_value = vmDhcpV4StaticBindingConfig(
            resource_type='DhcpV4StaticBindingConfig',
            id='test_segment-dhcpv4'
        )
        mock_update_binding_v6.return_value = vmDhcpV6StaticBindingConfig(
            resource_type='DhcpV6StaticBindingConfig',
            id='test_segment-dhcpv6'
        )
        mock_get_state_binding.return_value = {'state': 'success'}
        segment.add_static_bindings(network_unique_id='test_nic1',
                                    ip_v4_address='192.168.10.2',
                                    ip_v6_address='fc7e:f206:db42::')
        self.assertEqual(
            self._ctx.target.instance.runtime_properties[
                'dhcp_v4_static_binding_id'], 'test_segment-dhcpv4'
        )
        self.assertIsNotNone(
            self._ctx.target.instance.runtime_properties[
                'dhcp_v4_static_binding']
        )
        self.assertTrue(
            self._ctx.target.instance.runtime_properties[
                'tasks']['test_segment-dhcpv4']
        )
        self.assertEqual(
            self._ctx.target.instance.runtime_properties[
                'dhcp_v6_static_binding_id'], 'test_segment-dhcpv6'
        )
        self.assertIsNotNone(
            self._ctx.target.instance.runtime_properties[
                'dhcp_v6_static_binding']
        )
        self.assertTrue(
            self._ctx.target.instance.runtime_properties[
                'tasks']['test_segment-dhcpv6']
        )

    @mock.patch('nsx_t_sdk.resources.DhcpV6StaticBindingConfig.delete')
    @mock.patch('nsx_t_sdk.resources.DhcpV4StaticBindingConfig.delete')
    def test_remove_static_bindings(self,
                                    mock_delete_binding_v4,
                                    mock_delete_binding_v6,
                                    _):
        target = CustomMockContext({
            'instance': MockNodeInstanceContext(
                id='test_segment_wjkog',
                runtime_properties={
                    'dhcp_v4_static_binding_id': 'test_segment-dhcpv4',
                    'dhcp_v6_static_binding_id': 'test_segment-dhcpv6'
                }),
            'node': MockNodeContext(
                id='test_segment',
                properties={
                    'client_config': self.client_config,
                    'resource_config': self.resource_config,
                }
            ), '_context': {
                'node_id': 'test_segment'
            }})

        source = CustomMockContext({
            'instance': MockNodeInstanceContext(
                id='vpshere_server_okijw',
                runtime_properties={
                    'networks': [
                        {
                            'name': 'test_nic1',
                            'mac': 'test_mac1'
                        },
                        {
                            'name': 'test_nic2',
                            'mac': 'test_mac2'
                        }

                    ],
                    'id': 'vpshere_server_loki'
                }),
            'node': MockNodeContext(
                id='vpshere_server_loki',
                properties={
                    'client_config': self.client_config,
                    'resource_config': self.resource_config,
                }
            ), '_context': {
                'node_id': 'vpshere_server'
            }})
        self._set_context_operation(
            instance_type='relationship-instance',
            source=source,
            target=target,
            ctx_operation_name='cloudify.interfaces.'
                               'relationship_lifecycle.unlink',
            node_id='test_segment'
        )
        segment.remove_static_bindings()
        mock_delete_binding_v4.assert_called()
        mock_delete_binding_v6.assert_called()
