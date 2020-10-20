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
    Segment,
    SegmentPort,
    SegmentState
)
from nsx_t_sdk.exceptions import MethodNotAllowed
from nsx_t_sdk.common import (
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_GET,
    ACTION_LIST,
    ACTION_PATCH
)


class SegmentTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(SegmentTestCase, self).setUp()
        self.resource_config = {
            'id': 'segment_id',
            'display_name': 'segment_name'
        }
        self.segment = Segment(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_segment_client_config(self):
        self.assertEqual(self.segment.client_type, 'nsx_infra')
        self.assertEqual(self.segment.resource_type, 'Segment')
        self.assertEqual(self.segment.service_name, 'Segments')

    def test_segment_client_api_type(self):
        self.assertIsNotNone(
            self.segment._get_nsx_client_map()[self.segment.client_type]
        )

    def test_segment_allowed_actions(self):
        self.assertTrue(self.segment.allow_create)
        self.assertTrue(self.segment.allow_delete)
        self.assertTrue(self.segment.allow_get)
        self.assertTrue(self.segment.allow_list)
        self.assertTrue(self.segment.allow_update)
        self.assertTrue(self.segment.allow_patch)

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_create_segment(self, invoke_mock):
        self.segment.create()
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (self.segment.resource_id, self.segment.resource_config,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_update_segment(self, invoke_mock):
        self.segment.update('segment_id', {'display_name': 'updated_name'})
        invoke_mock.assert_called_with(
            ACTION_UPDATE,
            (self.segment.resource_id, {'display_name': 'updated_name'},)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_patch_segment(self, invoke_mock):
        self.segment.patch('segment_id', {'display_name': 'updated_name'})
        invoke_mock.assert_called_with(
            ACTION_PATCH,
            (self.segment.resource_id, {'display_name': 'updated_name'},)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_delete_segment(self, invoke_mock):
        self.segment.delete(self.segment.resource_id)
        invoke_mock.assert_called_with(
            ACTION_DELETE,
            (self.segment.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_segment(self, invoke_mock):
        self.segment.get()
        invoke_mock.assert_called_with(
            ACTION_GET,
            (self.segment.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_list_segment(self, invoke_mock):
        self.segment.list(filters={'id': self.segment.resource_id})
        filters = {
            'id': self.segment.resource_id,
            'cursor': None,
            'included_fields': None,
            'page_size': None,
            'sort_ascending': None,
            'sort_by': None

        }
        invoke_mock.assert_called_with(ACTION_LIST, kwargs=filters)


class SegmentPortTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(SegmentPortTestCase, self).setUp()
        self.resource_config = {
            'id': 'segment_port_id',
            'display_name': 'segment_port_name'
        }
        self.segment_port = SegmentPort(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_segment_port_client_config(self):
        self.assertEqual(self.segment_port.client_type, 'segment')
        self.assertEqual(self.segment_port.resource_type, 'Port')
        self.assertEqual(self.segment_port.service_name, 'Ports')

    def test_segment_port_client_api_type(self):
        self.assertIsNotNone(
            self.segment_port._get_nsx_client_map()
            [self.segment_port.client_type]
        )

    def test_segment_port_allowed_actions(self):
        self.assertFalse(self.segment_port.allow_create)
        self.assertTrue(self.segment_port.allow_delete)
        self.assertTrue(self.segment_port.allow_get)
        self.assertTrue(self.segment_port.allow_list)
        self.assertFalse(self.segment_port.allow_update)
        self.assertFalse(self.segment_port.allow_patch)

    def test_create_segment_port_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_port.create()

    def test_update_segment_port_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_port.update(
                'segment_port_id',
                {
                    'display_name':  'updated_segment_port_name'
                }
            )

    def test_patch_segment_port_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_port.patch(
                'segment_port_id',
                {
                    'display_name': 'updated_segment_port_name'
                }
            )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_delete_segment(self, invoke_mock):
        self.segment_port.delete(self.segment_port.resource_id)
        invoke_mock.assert_called_with(
            ACTION_DELETE,
            (self.segment_port.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_segment(self, invoke_mock):
        self.segment_port.get()
        invoke_mock.assert_called_with(
            ACTION_GET,
            (self.segment_port.resource_id,)
        )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_list_segment(self, invoke_mock):
        self.segment_port.list(filters={'id': self.segment_port.resource_id})
        filters = {
            'id': self.segment_port.resource_id,
            'cursor': None,
            'included_fields': None,
            'page_size': None,
            'sort_ascending': None,
            'sort_by': None

        }
        invoke_mock.assert_called_with(ACTION_LIST, kwargs=filters)


class SegmentStateTestCase(NSXTSDKTestCase):
    def setUp(self):
        super(SegmentStateTestCase, self).setUp()
        self.resource_config = {
            'id': 'segment_id',
            'display_name': 'segment_name'
        }
        self.segment_state = SegmentState(
            self.client_config,
            self.resource_config,
            self.logger
        )

    def test_segment_state_client_config(self):
        self.assertEqual(self.segment_state.client_type, 'segment')
        self.assertEqual(self.segment_state.resource_type, 'SegmentState')
        self.assertEqual(self.segment_state.service_name, 'State')

    def test_segment_state_client_api_type(self):
        self.assertIsNotNone(
            self.segment_state._get_nsx_client_map()
            [self.segment_state.client_type]
        )

    def test_segment_state_allowed_actions(self):
        self.assertFalse(self.segment_state.allow_create)
        self.assertFalse(self.segment_state.allow_delete)
        self.assertTrue(self.segment_state.allow_get)
        self.assertFalse(self.segment_state.allow_list)
        self.assertFalse(self.segment_state.allow_update)
        self.assertFalse(self.segment_state.allow_patch)

    def test_create_segment_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_state.create()

    def test_delete_segment_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_state.delete(
                self.segment_state.resource_id
            )

    def test_update_segment_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_state.update(
                'segment_port_id',
                {
                    'display_name':  'updated_segment_name'
                }
            )

    def test_patch_segment_state_not_allowed(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_state.patch(
                'segment_id',
                {
                    'display_name': 'updated_segment_name'
                }
            )

    def test_list_segment_state(self):
        with self.assertRaises(MethodNotAllowed):
            self.segment_state.list(
                filters={'id': self.segment_state.resource_id}
            )

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    def test_get_segment_state(self, invoke_mock):
        self.segment_state.get()
        invoke_mock.assert_called_with(
            ACTION_GET,
            (self.segment_state.resource_id,)
        )