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

# Third Parties Imports
import mock

from com.vmware.nsx_policy.model_client import (
    IpAddressInfo,
    VirtualMachineListResult,
    VirtualNetworkInterfaceListResult,
    VirtualMachine as vmVirtualMachine,
    VirtualNetworkInterface as vmVirtualNetworkInterface
)

from cloudify.exceptions import NonRecoverableError

# Local Imports
from nsx_t_plugin.tests.base import NSXTPluginTestBase
from nsx_t_plugin.virtual_machine import virtual_machine
from nsx_t_sdk.exceptions import NSXTSDKException


@mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client')
class VirtualMachineTestCase(NSXTPluginTestBase):

    @property
    def resource_config(self):
        return {
            'vm_name': 'test_vm_name',
            'network_id': 'test_segment_id'
        }

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_vm_from_inventory(self, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        mock_invoke.return_value = VirtualMachineListResult(results=[
            vmVirtualMachine(display_name='test_vm_name',
                             external_id='test_vm_name')
        ])
        virtual_machine.create()
        self.assertEqual(
            self._ctx.instance.runtime_properties['id'],
            'test_vm_name'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['name'],
            'test_vm_name'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['type'],
            virtual_machine.VirtualMachine.resource_type
        )

    def test_get_vm_from_inventory_with_missing_network_id(self, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties={
                'client_config': self.client_config,
                'resource_config': {
                    'vm_name': 'test_vm_name'
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        with self.assertRaises(NonRecoverableError):
            virtual_machine.create()

    def test_get_vm_from_inventory_with_missing_vm_id_or_name(self, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties={
                'client_config': self.client_config,
                'resource_config': {
                    'network_id': 'test_segment_id'
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        with self.assertRaises(NSXTSDKException):
            virtual_machine.create()

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_vm_from_inventory_with_empty_result(
            self,
            mock_invoke,
            _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        mock_invoke.return_value = VirtualMachineListResult(results=[])
        with self.assertRaises(NSXTSDKException):
            virtual_machine.create()

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_vm_from_inventory_with_multiple_results(
            self,
            mock_invoke,
            _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        mock_invoke.return_value = VirtualMachineListResult(results=[
            vmVirtualMachine(display_name='test_vm_name',
                             external_id='test_vm_name'),
            vmVirtualMachine(display_name='test_vm_name',
                             external_id='test_vm_name')
        ])
        with self.assertRaises(NSXTSDKException):
            virtual_machine.create()

    @mock.patch('nsx_t_plugin.virtual_machine.virtual_machine'
                '._lookup_segment_ports')
    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_configure(self, mock_invoke, mock_ports, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={'id': 'test_vm_name'},
            ctx_operation_name='cloudify.interfaces.lifecycle.configure')

        mock_ports.return_value = ['vim_port_id']
        mock_invoke.return_value = VirtualNetworkInterfaceListResult(
            results=[
                vmVirtualNetworkInterface(
                    ip_address_info=[
                        IpAddressInfo(
                            ip_addresses=['192.168.1.1', 'fc7e:f206:db42::'])
                    ],
                    display_name='test_nic1',
                    lport_attachment_id='vim_port_id'
                ),
                vmVirtualNetworkInterface(
                    ip_address_info=[
                        IpAddressInfo(
                            ip_addresses=[
                                '172.16.1.1',
                                '2001:db8::8a2e:370:7334'
                            ]
                        )
                    ],
                    display_name='test_nic2',
                )
            ]
        )
        virtual_machine.configure()
        self.assertTrue(
            'test_segment_id'
            in self._ctx.instance.runtime_properties
        )
        self.assertTrue(
            'networks'
            in self._ctx.instance.runtime_properties
        )
        self.assertTrue(
            'test_nic1' in self._ctx.instance.runtime_properties[
                'networks']['networks']
        )
        self.assertTrue(
            'test_nic2' in self._ctx.instance.runtime_properties[
                'networks']['networks']
        )
