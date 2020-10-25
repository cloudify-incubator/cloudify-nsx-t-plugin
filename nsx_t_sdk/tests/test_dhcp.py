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
import unittest

# Third parties imports
import mock

# Local imports
from nsx_t_sdk.tests.test_nsx_t_sdk import NSXTSDKTestCase
from nsx_t_sdk.resources import (
    DhcpServerConfig,
    DhcpV4StaticBindingConfig,
    DhcpV6StaticBindingConfig,
    DhcpStaticBindingState
)
from nsx_t_sdk.exceptions import MethodNotAllowed
from nsx_t_sdk.common import (
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_GET,
    ACTION_LIST,
    ACTION_PATCH
)


class DHCPServerConfigTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(DHCPServerConfigTestCase, self).setUp()
        self.resource_config = {
            'id': 'dhcp_server_config_id',
            'display_name': 'dhcp_server_config_name'
        }
        self.dhcp_server_config = DhcpServerConfig(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_dhcp_server_config_client_config(self):
        self.assertEqual(self.dhcp_server_config.client_type, 'nsx_infra')
        self.assertEqual(
            self.dhcp_server_config.resource_type,
            'DhcpServerConfig'
        )
        self.assertEqual(
            self.dhcp_server_config.service_name,
            'DhcpServerConfigs'
        )

    def test_dhcp_server_config_client_api_type(self):
        self.assertIsNotNone(
            self.dhcp_server_config._get_nsx_client_map()
            [self.dhcp_server_config.client_type]
        )

    def test_dhcp_server_config_allowed_actions(self):
        self.assertTrue(self.dhcp_server_config.allow_create)
        self.assertTrue(self.dhcp_server_config.allow_delete)
        self.assertTrue(self.dhcp_server_config.allow_get)
        self.assertTrue(self.dhcp_server_config.allow_list)
        self.assertTrue(self.dhcp_server_config.allow_update)
        self.assertTrue(self.dhcp_server_config.allow_patch)

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_create_dhcp_server_config(self, invoke_mock):
        self.dhcp_server_config.create()
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (self.dhcp_server_config.resource_id,
             self.dhcp_server_config.resource_config,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_update_dhcp_server_config(self, invoke_mock):
        self.dhcp_server_config.update(
            'dhcp_server_config_id', {'display_name': 'updated_name'})
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (self.dhcp_server_config.resource_id,
             {'display_name': 'updated_name'},)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_patch_dhcp_server_config(self, invoke_mock):
        self.dhcp_server_config.patch(
            'dhcp_server_config_id', {'display_name': 'updated_name'})
        invoke_mock.assert_called_with(
            ACTION_PATCH,
            (self.dhcp_server_config.resource_id,
             {'display_name': 'updated_name'},)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_delete_dhcp_server_config(self, invoke_mock):
        self.dhcp_server_config.delete(self.dhcp_server_config.resource_id)
        invoke_mock.assert_called_with(
            ACTION_DELETE,
            (self.dhcp_server_config.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_dhcp_server_config(self, invoke_mock):
        self.dhcp_server_config.get()
        invoke_mock.assert_called_with(
            ACTION_GET,
            (self.dhcp_server_config.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_list_dhcp_server_config(self, invoke_mock):
        self.dhcp_server_config.list(
            filters={'id': self.dhcp_server_config.resource_id})
        filters = {
            'id': self.dhcp_server_config.resource_id,
            'cursor': None,
            'included_fields': None,
            'page_size': None,
            'sort_ascending': None,
            'sort_by': None

        }
        invoke_mock.assert_called_with(ACTION_LIST, kwargs=filters)


class DHCPStaticBindingConfig(unittest.TestCase):
    def _test_dhcp_static_binding_client(self,
                                         dhcp_static_binding,
                                         resource_type):
        self.assertEqual(dhcp_static_binding.client_type, 'segment')
        self.assertEqual(dhcp_static_binding.resource_type, resource_type)
        self.assertEqual(dhcp_static_binding.service_name,
                         'DhcpStaticBindingConfigs')

    def _test_dhcp_static_binding_client_api_type(self, dhcp_static_binding):
        self.assertIsNotNone(
            dhcp_static_binding._get_nsx_client_map()
            [dhcp_static_binding.client_type]
        )

    def _test_dhcp_static_binding_allowed_actions(self, dhcp_static_binding):
        self.assertTrue(dhcp_static_binding.allow_create)
        self.assertTrue(dhcp_static_binding.allow_delete)
        self.assertTrue(dhcp_static_binding.allow_get)
        self.assertTrue(dhcp_static_binding.allow_list)
        self.assertTrue(dhcp_static_binding.allow_update)
        self.assertTrue(dhcp_static_binding.allow_patch)

    @staticmethod
    def _test_create_dhcp_static_binding_config(invoke_mock,
                                                dhcp_static_binding):
        dhcp_static_binding.create()
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (dhcp_static_binding.resource_id,
             dhcp_static_binding.resource_config,)
        )

    @staticmethod
    def _test_update_dhcp_static_binding_config(
            invoke_mock,
            dhcp_static_binding,
            dhcp_static_binding_config):

        dhcp_static_binding.update(
            dhcp_static_binding.resource_id, dhcp_static_binding_config)
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (dhcp_static_binding.resource_id,
             dhcp_static_binding_config,)
        )

    @staticmethod
    def _test_patch_dhcp_static_binding_config(
            invoke_mock,
            dhcp_static_binding,
            dhcp_static_binding_config):

        dhcp_static_binding.patch(
            dhcp_static_binding.resource_id, dhcp_static_binding_config)
        invoke_mock.assert_called_with(
            ACTION_PATCH,
            (dhcp_static_binding.resource_id,
             dhcp_static_binding_config,)
        )

    @staticmethod
    def _test_get_dhcp_static_binding_config(
            invoke_mock,
            dhcp_static_binding):
        dhcp_static_binding.get()
        invoke_mock.assert_called_with(
            ACTION_GET,
            (dhcp_static_binding.resource_id,)
        )

    @staticmethod
    def _test_list_dhcp_static_binding_config(
            invoke_mock,
            dhcp_static_binding):

        dhcp_static_binding.list(
            filters={'id': dhcp_static_binding.resource_id})
        filters = {
            'id': dhcp_static_binding.resource_id,
            'cursor': None,
            'included_fields': None,
            'page_size': None,
            'sort_ascending': None,
            'sort_by': None

        }
        invoke_mock.assert_called_with(ACTION_LIST, kwargs=filters)


class DHCPV4StaticBindingTestCase(DHCPStaticBindingConfig, NSXTSDKTestCase):
    def setUp(self):
        super(DHCPV4StaticBindingTestCase, self).setUp()
        self.resource_config = {
            'id': 'dhcp_v4_static_binding_id',
            'display_name': 'dhcp_v4_static_binding_name'
        }
        self.dhcp_v4_static_binding = DhcpV4StaticBindingConfig(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_dhcp_v4_static_binding_client(self):
        self._test_dhcp_static_binding_client(
            self.dhcp_v4_static_binding,
            'DhcpV4StaticBindingConfig'
        )

    def test_dhcp_v4_static_binding_client_api_type(self):
        self._test_dhcp_static_binding_client_api_type(
            self.dhcp_v4_static_binding
        )

    def test_dhcp_v4_static_binding_allowed_actions(self):
        self._test_dhcp_static_binding_allowed_actions(
            self.dhcp_v4_static_binding
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_create_dhcp_v4_static_binding(self, invoke_mock):
        self._test_create_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v4_static_binding
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_update_dhcp_v4_static_binding(self, invoke_mock):
        self._test_update_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v4_static_binding,
            {'display_name': 'updated_dhcp_v4_static_binding_name'}
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_dhcp_v4_static_binding(self, invoke_mock):
        self._test_get_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v4_static_binding
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_list_dhcp_v4_static_binding(self, invoke_mock):
        self._test_list_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v4_static_binding
        )


class DHCPV6StaticBindingTestCase(DHCPStaticBindingConfig, NSXTSDKTestCase):
    def setUp(self):
        super(DHCPV6StaticBindingTestCase, self).setUp()
        self.resource_config = {
            'id': 'dhcp_v6_static_binding_id',
            'display_name': 'dhcp_v6_static_binding_name'
        }
        self.dhcp_v6_static_binding = DhcpV6StaticBindingConfig(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_dhcp_v6_static_binding_client(self):
        self._test_dhcp_static_binding_client(
            self.dhcp_v6_static_binding,
            'DhcpV6StaticBindingConfig'
        )

    def test_dhcp_v6_static_binding_client_api_type(self):
        self._test_dhcp_static_binding_client_api_type(
            self.dhcp_v6_static_binding
        )

    def test_dhcp_v6_static_binding_allowed_actions(self):
        self._test_dhcp_static_binding_allowed_actions(
            self.dhcp_v6_static_binding
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_create_dhcp_v6_static_binding(self, invoke_mock):
        self._test_create_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v6_static_binding
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_update_dhcp_v6_static_binding(self, invoke_mock):
        self._test_update_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v6_static_binding,
            {'display_name': 'updated_dhcp_v6_static_binding_name'}
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_dhcp_v6_static_binding(self, invoke_mock):
        self._test_get_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v6_static_binding
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_list_dhcp_v6_static_binding(self, invoke_mock):
        self._test_list_dhcp_static_binding_config(
            invoke_mock,
            self.dhcp_v6_static_binding
        )


class DhcpStaticBindingStateTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(DhcpStaticBindingStateTestCase, self).setUp()
        self.resource_config = {}
        self.dhcp_static_binding_state = DhcpStaticBindingState(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_dhcp_static_binding_state_client_config(self):
        self.assertEqual(
            self.dhcp_static_binding_state.client_type,
            'dhcp_static_bindings'
        )
        self.assertEqual(
            self.dhcp_static_binding_state.resource_type,
            'DhcpStaticBindingState'
        )
        self.assertEqual(self.dhcp_static_binding_state.service_name, 'State')

    def test_dhcp_static_binding_state_client_api_type(self):
        self.assertIsNotNone(
            self.dhcp_static_binding_state._get_nsx_client_map()
            [self.dhcp_static_binding_state.client_type]
        )

    def test_dhcp_static_binding_state_allowed_actions(self):
        self.assertFalse(self.dhcp_static_binding_state.allow_create)
        self.assertFalse(self.dhcp_static_binding_state.allow_delete)
        self.assertTrue(self.dhcp_static_binding_state.allow_get)
        self.assertFalse(self.dhcp_static_binding_state.allow_list)
        self.assertFalse(self.dhcp_static_binding_state.allow_update)
        self.assertFalse(self.dhcp_static_binding_state.allow_patch)

    def test_create_dhcp_static_binding_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.dhcp_static_binding_state.create()

    def test_delete_dhcp_static_binding_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.dhcp_static_binding_state.delete(
                self.dhcp_static_binding_state.resource_id
            )

    def test_update_dhcp_static_binding_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.dhcp_static_binding_state.update(
                'dhcp_static_binding_id',
                {
                    'foo':  'bar'
                }
            )

    def test_patch_dhcp_static_binding_state_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.dhcp_static_binding_state.patch(
                'dhcp_static_binding_id',
                {
                    'foo': 'bar'
                }
            )

    def test_list_dhcp_static_binding_state(self):
        with self.assertRaises(MethodNotAllowed):
            self.dhcp_static_binding_state.list(
                filters={'id': self.dhcp_static_binding_state.resource_id}
            )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_dhcp_static_binding_state(self, invoke_mock):
        self.dhcp_static_binding_state.resource_id = 'dhcp_static_binding_id'
        self.dhcp_static_binding_state.get(
            args=('segment_id', self.dhcp_static_binding_state.resource_id,))
        invoke_mock.assert_called_with(
            ACTION_GET,
            ('segment_id', self.dhcp_static_binding_state.resource_id,)
        )
