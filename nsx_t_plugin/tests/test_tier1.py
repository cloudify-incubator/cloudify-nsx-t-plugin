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
    Tier1 as vmTier1,
    Tier1GatewayState,
    LogicalRouterState
)
from com.vmware.vapi.std.errors_client import Error, NotFound

from cloudify.exceptions import NonRecoverableError, OperationRetry

# Local Imports
from nsx_t_plugin.tests.base import NSXTPluginTestBase
from nsx_t_plugin.tier1 import tier1


@mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client')
class Tier1TestCase(NSXTPluginTestBase):

    @property
    def resource_config(self):
        config = {
            'id': 'test_tier1',
            'display_name': 'Test Tier1 Router',
            'description': 'Test Tier1 Router',
            'tier0_path': '/infra/tier-0s/tier0'
        }
        return config

    @mock.patch('nsx_t_sdk.common.NSXTResource._invoke')
    @mock.patch('nsx_t_sdk.resources.DhcpServerConfig.create')
    def test_create_tier1(self, mock_create, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.create')

        res = copy.deepcopy(self.resource_config)
        res['path'] = '/test/path/tier1-config'
        mock_create.return_value = vmTier1(**res)
        mock_invoke.return_value = vmTier1(**res)
        tier1.create()

        self.assertEqual(
            self._ctx.instance.runtime_properties['id'],
            'test_tier1'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['name'],
            'Test Tier1 Router'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['type'],
            tier1.Tier1.resource_type
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['path'],
            '/test/path/tier1-config'
        )

    @mock.patch('nsx_t_sdk.resources.NSXTResource._invoke')
    def test_start_tier1_on_success(self, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={
                'id': 'test_tier1',
                'type': tier1.Tier1state.resource_type,
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        mock_invoke.return_value = Tier1GatewayState(
            tier1_state=LogicalRouterState(state='success'))
        tier1.start()

    @mock.patch('nsx_t_sdk.resources.NSXTResource._invoke')
    def test_start_tier1_on_pending(self, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={
                'id': 'test_tier1',
                'type': tier1.Tier1state.resource_type,
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        mock_invoke.return_value = Tier1GatewayState(
            tier1_state=LogicalRouterState(state='pending'))
        with self.assertRaises(OperationRetry):
            tier1.start()

    @mock.patch('nsx_t_sdk.resources.NSXTResource._invoke')
    def test_start_tier1_on_failed(self, mock_invoke, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={
                'id': 'test_tier1',
                'type': tier1.Tier1state.resource_type,
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        mock_invoke.return_value = Tier1GatewayState(
            tier1_state=LogicalRouterState(state='failed'))
        with self.assertRaises(NonRecoverableError):
            tier1.start()

    @mock.patch('nsx_t_sdk.resources.Tier1.delete')
    @mock.patch('nsx_t_sdk.resources.Tier1.get')
    def test_delete_tier1(self, mock_get, mock_delete, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={
                'id': 'test_tier1',
                'name': 'Test Tier1 Router',
                'type': tier1.Tier1.resource_type,
                'path': '/test/path/tier1-config'
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_delete.return_value = None
        mock_get.return_value = vmTier1(id='test_tier1')
        with self.assertRaises(OperationRetry):
            tier1.delete()

    @mock.patch('nsx_t_sdk.resources.Tier1.delete')
    @mock.patch('nsx_t_sdk.resources.Tier1.get')
    def test_delete_tier1_with_error(self, mock_get, mock_delete, _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={
                'id': 'test_tier1',
                'name': 'Test Tier1 Router',
                'type': tier1.Tier1.resource_type,
                'path': '/test/path/tier1-config'
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_delete.side_effect = Error
        mock_get.return_value = vmTier1(id='test_tier1')
        with self.assertRaises(OperationRetry):
            tier1.delete()

    @mock.patch('nsx_t_sdk.resources.Tier1.get')
    def test_delete_tier1_in_progress_with_success(
            self,
            mock_get,
            _):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            test_runtime_properties={
                'id': 'test_tier1',
                'name': 'Test Tier1 Router',
                'type': tier1.Tier1.resource_type,
                'path': '/test/path/tier1-config'
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')
        mock_get.side_effect = NotFound
        tier1.delete()
