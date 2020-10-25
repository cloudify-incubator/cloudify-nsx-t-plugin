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
import requests
import mock

# Local imports
from nsx_t_sdk.common import NSXTResource


class MockSessionResponse(object):
    def __init__(self, status_code):
        self.status_code = status_code
        self.headers = {}

    def raise_for_status(self):
        raise requests.HTTPError('HTTP Error')


class NSXTSDKTestCase(unittest.TestCase):
    def setUp(self):
        super(NSXTSDKTestCase, self).setUp()
        self.client_config = {
            'username': 'foo',
            'password': 'bar',
            'host': 'foo-host',
            'port': '80',
            'insecure': False,
            'auth_type': 'basic'
        }
        self.logger = mock.MagicMock()

    @mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client')
    def test_nsx_t_client_config(self, _):
        client = NSXTResource(
            self.client_config, {
                'id': 'resource_id',
                'display_name': 'resource_id'
            },
            self.logger
        )
        self.assertEqual(self.client_config['username'], client.username)
        self.assertEqual(self.client_config['password'], client.password)
        self.assertEqual(self.client_config['host'], client.host)
        self.assertEqual(self.client_config['port'], client.port)
        self.assertEqual(self.client_config['insecure'], client.insecure)
        self.assertEqual(self.client_config['auth_type'], client.auth_type)
        self.assertEqual(
            client.url,
            'https://{0}:{1}'.format(client.host, client.port)
        )
        self.assertFalse(client.insecure)
        self.assertIsNone(client.cert)

    @mock.patch('nsx_t_sdk.common.NSXTResource._get_nsx_client_map')
    def test_api_client_instance(self, _):
        client = NSXTResource(
            self.client_config, {
                'id': 'resource_id',
                'display_name': 'resource_id'
            },
            self.logger
        )
        self.assertIsNotNone(client._api_client)

    def test_get_invalid_nsx_t_client(self):
        result = NSXTResource._get_nsx_client_map().get('invalid_client')
        self.assertIsNone(result)

    def test_get_valid_nsx_t_client(self):
        client_keys = [
            'nsx',
            'nsx_policy',
            'nsx_infra',
            'segment',
            'tier_1',
            'fabric',
            'dhcp_static_bindings'
        ]
        for key in NSXTResource._get_nsx_client_map():
            self.assertIn(key, client_keys)

    @mock.patch('nsx_t_sdk.common.NSXTResource._get_nsx_client_map')
    @mock.patch('nsx_t_sdk.common.NSXTResource._prepare_basic_auth')
    def test_nsx_t_client_with_basic_auth(self, prepare_basic_auth_mock, _):
        _ = NSXTResource(
            self.client_config, {
                'id': 'resource_id',
                'display_name': 'resource_id'
            },
            self.logger
        )
        self.assertTrue(prepare_basic_auth_mock.called)

    @mock.patch('nsx_t_sdk.common.NSXTResource._get_nsx_client_map')
    @mock.patch('nsx_t_sdk.common.NSXTResource._prepare_session_auth')
    def test_nsx_t_client_with_session_auth(
            self, prepare_session_auth_mock, _):
        self.client_config['auth_type'] = 'session'
        _ = NSXTResource(
            self.client_config, {
                'id': 'resource_id',
                'display_name': 'resource_id'
            },
            self.logger
        )
        self.assertTrue(prepare_session_auth_mock.called)

    @mock.patch('nsx_t_sdk.common.NSXTResource._get_nsx_client_map')
    @mock.patch.object(requests.Session, 'post',
                       return_value=MockSessionResponse(status_code=400))
    def test_invalid_session_requests(self, *_):
        self.client_config['auth_type'] = 'session'
        with self.assertRaises(requests.HTTPError):
            _ = NSXTResource(
                self.client_config, {
                    'id': 'resource_id',
                    'display_name': 'resource_id'
                },
                self.logger
            )

    @mock.patch('nsx_t_sdk.common.NSXTResource'
                '._get_stub_factory_for_nsx_client')
    @mock.patch('nsx_t_sdk.common.NSXTResource._get_nsx_client_map')
    @mock.patch('nsx_t_sdk.common.requests.Session.post')
    def test_valid_session_requests(
            self,
            post_mock,
            client_map_mock,
            factory_mock):
        post_mock.return_value = MockSessionResponse(status_code=200)
        self.client_config['auth_type'] = 'session'
        NSXTResource(
            self.client_config, {
                'id': 'resource_id',
                'display_name': 'resource_id'
            },
            self.logger
        )
