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

from cloudify.state import current_ctx
from cloudify.exceptions import NonRecoverableError, OperationRetry

# Local Imports
from nsx_t_plugin.tests.base import (
    NSXTPluginTestBase,
    CustomMockContext,
    MockNodeInstanceContext,
    MockNodeContext
)

from nsx_t_sdk.resources import NSXTResource

from nsx_t_plugin.utils import (
    get_ctx_object,
    populate_nsx_t_instance_from_ctx,
    delete_runtime_properties_from_instance,
    set_basic_runtime_properties_for_instance,
    update_runtime_properties_for_instance,
    validate_if_resource_started
)


class UtilsTestCase(NSXTPluginTestBase):

    def test_get_context_object(self):
        self._set_context_operation()
        self.assertTrue(get_ctx_object(self._ctx) is self._ctx)

        # Clear context to prepare for another one
        current_ctx.clear()
        target = CustomMockContext({
            'instance': MockNodeInstanceContext(
                id='node-1',
                runtime_properties={

                }),
            'node': MockNodeContext(
                id='1',
                properties={
                    'client_config': self.client_config,
                    'resource_config': self.resource_config,
                }
            ), '_context': {
                'node_id': '1'
            }})

        source = CustomMockContext({
            'instance': MockNodeInstanceContext(
                id='node-2',
                runtime_properties={
                }),
            'node': MockNodeContext(
                id='2',
                properties={
                    'client_config': self.client_config,
                    'resource_config': self.resource_config,
                }
            ), '_context': {
                'node_id': '2'
            }})
        self._set_context_operation(
            instance_type='relationship-instance',
            source=source,
            target=target,
            node_id='1'
        )
        get_ctx_object(self._ctx)
        self.assertFalse(get_ctx_object(self._ctx) is self._ctx)
        current_ctx.clear()

    @mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client')
    def test_populate_nsx_t_instance_from_ctx(self, _):
        self._set_context_operation()
        obj = populate_nsx_t_instance_from_ctx(NSXTResource, self._ctx, {})
        self.assertEqual(
            obj.client_config,
            self.node_properties['client_config']
        )
        self.assertEqual(
            obj.resource_id,
            self.node_properties['resource_config']['id']
        )
        self.assertEqual(
            obj.resource_config['display_name'],
            self.node_properties['resource_config']['display_name']
        )
        self.assertEqual(
            obj.resource_config['description'],
            self.node_properties['resource_config']['description']
        )
        current_ctx.clear()

    def test_delete_runtime_properties_from_instance(self):
        self._set_context_operation(
            runtime_properties={'foo': 'bar', 'foo2': 'bar2'})

        self.assertTrue(len(self._ctx.instance.runtime_properties) > 1)
        delete_runtime_properties_from_instance(self._ctx)
        self.assertFalse(len(self._ctx.instance.runtime_properties) > 1)
        current_ctx.clear()

    def test_set_basic_runtime_properties_for_instance(self):
        self._set_context_operation(
            runtime_properties={'foo': 'bar', 'foo2': 'bar2'})

        resource = mock.Mock(
            resource_type='foo_resource',
            resource_id='test_resource_id'
        )
        resource.get = mock.Mock(
            return_value={'display_name': 'test_resource'}
        )
        set_basic_runtime_properties_for_instance(resource, self._ctx)
        self.assertEqual(
            self._ctx.instance.runtime_properties['type'],
            'foo_resource'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['id'],
            'test_resource_id'
        )
        self.assertEqual(
            self._ctx.instance.runtime_properties['resource_config'],
            {'display_name': 'test_resource'}
        )
        current_ctx.clear()

    @mock.patch('nsx_t_plugin.utils.delete_runtime_properties_from_instance')
    @mock.patch('nsx_t_plugin.utils.set_basic_runtime_properties_for_instance')
    def test_update_runtime_properties_for_instance(self,
                                                    mock_set,
                                                    mock_delete):
        operation = 'cloudify.interfaces.lifecycle.create'
        self._set_context_operation(
            ctx_operation_name=operation
        )
        resource = mock.Mock()
        update_runtime_properties_for_instance(resource, self._ctx, operation)
        mock_set.assert_called()

        resource.reset_mock()
        current_ctx.clear()
        operation = 'cloudify.interfaces.lifecycle.delete'
        self._set_context_operation(
            ctx_operation_name=operation
        )
        update_runtime_properties_for_instance(resource, self._ctx, operation)
        mock_delete.assert_called()
        current_ctx.clear()

    def test_resource_in_pending_state(self):
        nsx_t_state = mock.Mock(state_attr='state')
        pending_states = ['pending']
        ready_states = ['started']
        nsx_t_state.get = mock.Mock(return_value={'state': 'pending'})
        with self.assertRaises(OperationRetry):
            validate_if_resource_started(
                'foo_resource',
                nsx_t_state,
                pending_states,
                ready_states
            )

    def test_resource_in_failed_state(self):
        nsx_t_state = mock.Mock(state_attr='state')
        pending_states = ['pending']
        ready_states = ['started']
        nsx_t_state.get = mock.Mock(return_value={'state': 'failed'})
        with self.assertRaises(NonRecoverableError):
            validate_if_resource_started(
                'foo_resource',
                nsx_t_state,
                pending_states,
                ready_states
            )

    def test_resource_in_started_state(self):
        self._set_context_operation()
        nsx_t_state = mock.Mock(state_attr='state')
        pending_states = ['pending']
        ready_states = ['started']
        nsx_t_state.get = mock.Mock(return_value={'state': 'started'})
        validate_if_resource_started(
            'foo_resource',
            nsx_t_state,
            pending_states,
            ready_states
        )
