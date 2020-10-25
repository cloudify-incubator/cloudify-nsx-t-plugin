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
    Tier1,
    Tier1state
)
from nsx_t_sdk.exceptions import MethodNotAllowed
from nsx_t_sdk.common import (
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_GET,
    ACTION_LIST,
    ACTION_PATCH
)


class Tier1TestCase(NSXTSDKTestCase):
    def setUp(self):
        super(Tier1TestCase, self).setUp()
        self.resource_config = {
            'id': 'tier1_id',
            'display_name': 'tier1_name'
        }
        self.tier1 = Tier1(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_tier1_client_config(self):
        self.assertEqual(self.tier1.client_type, 'nsx_infra')
        self.assertEqual(self.tier1.resource_type, 'Tier1')
        self.assertEqual(self.tier1.service_name, 'Tier1s')

    def test_tier1_client_api_type(self):
        self.assertIsNotNone(
            self.tier1._get_nsx_client_map()[self.tier1.client_type]
        )

    def test_tier1_allowed_actions(self):
        self.assertTrue(self.tier1.allow_create)
        self.assertTrue(self.tier1.allow_delete)
        self.assertTrue(self.tier1.allow_get)
        self.assertTrue(self.tier1.allow_list)
        self.assertTrue(self.tier1.allow_update)
        self.assertTrue(self.tier1.allow_patch)

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_create_tier1(self, invoke_mock):
        self.tier1.create()
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (self.tier1.resource_id, self.tier1.resource_config,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_update_tier1(self, invoke_mock):
        self.tier1.update('tier1_id', {'display_name': 'updated_name'})
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (self.tier1.resource_id, {'display_name': 'updated_name'},)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_patch_tier1(self, invoke_mock):
        self.tier1.patch('tier1_id', {'display_name': 'updated_name'})
        invoke_mock.assert_called_with(
            ACTION_PATCH,
            (self.tier1.resource_id, {'display_name': 'updated_name'},)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_delete_tier1(self, invoke_mock):
        self.tier1.delete(self.tier1.resource_id)
        invoke_mock.assert_called_with(
            ACTION_DELETE,
            (self.tier1.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_tier1(self, invoke_mock):
        self.tier1.get()
        invoke_mock.assert_called_with(
            ACTION_GET,
            (self.tier1.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_list_tier1(self, invoke_mock):
        self.tier1.list(filters={'id': self.tier1.resource_id})
        filters = {
            'id': self.tier1.resource_id,
            'cursor': None,
            'included_fields': None,
            'page_size': None,
            'sort_ascending': None,
            'sort_by': None

        }
        invoke_mock.assert_called_with(ACTION_LIST, kwargs=filters)


class Tier1stateTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(Tier1stateTestCase, self).setUp()
        self.resource_config = {
            'id': 'tier1_id'
        }
        self.tier1_state = Tier1state(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_tier1_state_client_config(self):
        self.assertEqual(self.tier1_state.client_type, 'tier_1')
        self.assertEqual(self.tier1_state.resource_type, 'Tier1State')
        self.assertEqual(self.tier1_state.service_name, 'State')

    def test_tier1_state_client_api_type(self):
        self.assertIsNotNone(
            self.tier1_state._get_nsx_client_map()
            [self.tier1_state.client_type]
        )

    def test_tier1_state_allowed_actions(self):
        self.assertFalse(self.tier1_state.allow_create)
        self.assertFalse(self.tier1_state.allow_delete)
        self.assertTrue(self.tier1_state.allow_get)
        self.assertFalse(self.tier1_state.allow_list)
        self.assertFalse(self.tier1_state.allow_update)
        self.assertFalse(self.tier1_state.allow_patch)

    def test_create_tier1_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.tier1_state.create()

    def test_delete_tier1_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.tier1_state.delete(
                self.tier1_state.resource_id
            )

    def test_update_tier1_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.tier1_state.update(
                'tier1_id',
                {
                    'display_name':  'updated_tier1_name'
                }
            )

    def test_patch_tier1_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.tier1_state.patch(
                'tier1_id',
                {
                    'display_name': 'updated_tier1_name'
                }
            )

    def test_list_tier1_state(self):
        with self.assertRaises(MethodNotAllowed):
            self.tier1_state.list(
                filters={'id': self.tier1_state.resource_id}
            )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_tier1_state(self, invoke_mock):
        self.tier1_state.get()
        invoke_mock.assert_called_with(
            ACTION_GET,
            (self.tier1_state.resource_id,)
        )
