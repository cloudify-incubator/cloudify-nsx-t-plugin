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

# Third parties imports
import mock

# Local imports
from nsx_t_sdk.tests.test_nsx_t_sdk import NSXTSDKTestCase
from nsx_t_sdk.resources import (
    VirtualNetworkInterface,
    VirtualMachine
)
from nsx_t_sdk.exceptions import MethodNotAllowed
from nsx_t_sdk.common import (
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_GET,
    ACTION_LIST,
    ACTION_PATCH
)


class VirtualMachineTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(VirtualMachineTestCase, self).setUp()
        self.resource_config = {
            'vm_name': 'test_vm',
            'network_id': 'test_network_id'
        }
        self.virtual_machine = VirtualMachine(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_virtual_machine_client_config(self):
        self.assertEqual(self.virtual_machine.client_type, 'fabric')
        self.assertEqual(self.virtual_machine.resource_type, 'VirtualMachine')
        self.assertEqual(self.virtual_machine.service_name, 'VirtualMachines')

    def test_virtual_machine_client_api_type(self):
        self.assertIsNotNone(
            self.virtual_machine._get_nsx_client_map()
            [self.virtual_machine.client_type]
        )

    def test_virtual_machine_allowed_actions(self):
        self.assertFalse(self.virtual_machine.allow_create)
        self.assertTrue(self.virtual_machine.allow_delete)
        self.assertTrue(self.virtual_machine.allow_get)
        self.assertTrue(self.virtual_machine.allow_list)
        self.assertFalse(self.virtual_machine.allow_update)
        self.assertFalse(self.virtual_machine.allow_patch)

    def test_create_virtual_machine_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.virtual_machine.create()

    def test_update_virtual_machine_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.virtual_machine.update(
                'virtual_machine_id',
                {
                    'foo':  'bar'
                }
            )

    def test_patch_virtual_machine_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.virtual_machine.patch(
                'virtual_machine_id',
                {
                    'foo':  'bar'
                }
            )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_delete_virtual_machine(self, invoke_mock):
        self.virtual_machine.delete(
            self.virtual_machine.resource_config['vm_name']
        )
        invoke_mock.assert_called_with(
            ACTION_DELETE,
            (self.virtual_machine.resource_config['vm_name'],)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_virtual_machine(self, invoke_mock):
        self.virtual_machine.get(
            args=(self.virtual_machine.resource_config['vm_name'],)
        )
        filters = {
            'display_name': self.virtual_machine.resource_config['vm_name'],
            'external_id': None,
            'cursor': None,
            'included_fields': None,
            'page_size': None,
            'sort_ascending': None,
            'sort_by': None

        }
        invoke_mock.assert_called_with(ACTION_LIST, kwargs=filters)


class VirtualNetworkInterfaceTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(VirtualNetworkInterfaceTestCase, self).setUp()
        self.resource_config = {
            'id': 'test_vm_id',
        }
        self.virtual_network_interface = VirtualNetworkInterface(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_virtual_network_interface_client_config(self):
        self.assertEqual(
            self.virtual_network_interface.client_type,
            'fabric'
        )
        self.assertEqual(
            self.virtual_network_interface.resource_type,
            'VirtualNetworkInterface'
        )
        self.assertEqual(self.virtual_network_interface.service_name, 'Vifs')

    def test_virtual_network_interface_client_api_type(self):
        self.assertIsNotNone(
            self.virtual_network_interface._get_nsx_client_map()
            [self.virtual_network_interface.client_type]
        )

    def test_virtual_network_interface_allowed_actions(self):
        self.assertFalse(self.virtual_network_interface.allow_create)
        self.assertTrue(self.virtual_network_interface.allow_delete)
        self.assertFalse(self.virtual_network_interface.allow_get)
        self.assertTrue(self.virtual_network_interface.allow_list)
        self.assertFalse(self.virtual_network_interface.allow_update)
        self.assertFalse(self.virtual_network_interface.allow_patch)

    def test_create_virtual_network_interface_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.virtual_network_interface.create()

    def test_update_virtual_network_interface_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.virtual_network_interface.update(
                'virtual_network_interface_id',
                {
                    'foo':  'bar'
                }
            )

    def test_patch_virtual_network_interface_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.virtual_network_interface.patch(
                'virtual_machine_id',
                {
                    'foo':  'bar'
                }
            )

    def test_get_virtual_network_interface_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.virtual_network_interface.get()

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_list_virtual_network_interface(self, invoke_mock):
        self.virtual_network_interface.list(
            filters={'owner_vm_id': 'test_vm_id'})
        filters = {
            'owner_vm_id': 'test_vm_id',
            'cursor': None,
            'included_fields': None,
            'page_size': None,
            'sort_ascending': None,
            'sort_by': None

        }
        invoke_mock.assert_called_with(ACTION_LIST, kwargs=filters)
