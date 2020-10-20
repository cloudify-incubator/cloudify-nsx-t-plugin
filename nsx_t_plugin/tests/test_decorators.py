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
from cloudify.exceptions import NonRecoverableError

# Local Imports
from nsx_t_plugin.tests.base import (
    CustomMockContext,
    MockNodeInstanceContext,
    MockNodeContext
)
from nsx_t_plugin.tests.base import NSXTPluginTestBase
from nsx_t_plugin.decorators import with_nsx_t_client
from nsx_t_sdk.resources import NSXTResource


class DecoratorTestCase(NSXTPluginTestBase):

    def test_create_or_delete_with_nsx_t_client(self):
        # Test create operation with decorator
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.create')
        func = mock.Mock()
        func.__name__ = 'foo_func'
        with mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client'):
            with mock.patch(
                    'nsx_t_plugin.utils'
                    '.set_basic_runtime_properties_for_instance'
            ) as mock_set:
                with_nsx_t_client(NSXTResource)(func)()
                mock_set.assert_called()
                func.assert_called()

        func.reset_mock()
        current_ctx.clear()

        # Test delete operation with decorator
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')

        func = mock.Mock()
        func.__name__ = 'foo_func'
        with mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client'):
            with mock.patch(
                    'nsx_t_plugin.utils'
                    '.delete_runtime_properties_from_instance'
            ) as mock_delete:
                with_nsx_t_client(NSXTResource)(func)()
                mock_delete.assert_called()
                func.assert_called()

    @mock.patch('nsx_t_plugin.utils.delete_runtime_properties_from_instance')
    @mock.patch('nsx_t_plugin.utils.set_basic_runtime_properties_for_instance')
    def test_other_operations_with_nsx_t_client(self, mock_set, mock_delete):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='foo.operation')
        func = mock.Mock()
        func.__name__ = 'foo_func'
        with mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client'):
            with_nsx_t_client(NSXTResource)(func)()
            mock_set.assert_not_called()
            mock_delete.assert_not_called()
            func.assert_called()

    @mock.patch('nsx_t_plugin.utils.get_relationship_subject_context')
    @mock.patch('nsx_t_plugin.utils.delete_runtime_properties_from_instance')
    @mock.patch('nsx_t_plugin.utils.set_basic_runtime_properties_for_instance')
    def test_relationship_operations_with_nsx_t_client(
            self, mock_set, mock_delete, mock_rel):
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

        self._pepare_relationship_context_for_operation(
            deployment_id='foo-deployment',
            source=source,
            target=target,
            ctx_operation_name='cloudify.interfaces.'
                               'relationship_lifecycle.establish',
            node_id='1'
        )
        func = mock.Mock()
        func.__name__ = 'foo_func'
        with mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client'):
            with_nsx_t_client(NSXTResource)(func)()
            mock_rel.assert_called()
            mock_set.assert_not_called()
            mock_delete.assert_not_called()
            func.assert_called()

    def test_raise_exception_with_nsx_t_client(self):
        self._prepare_context_for_operation(
            test_name='NodeInstanceContext',
            test_properties=self.node_properties,
            ctx_operation_name='foo.operation')
        func = mock.Mock()
        func.__name__ = 'foo_func'
        func.side_effect = Exception('Some Exception')
        with mock.patch('nsx_t_sdk.common.NSXTResource._prepare_nsx_t_client'):
            with self.assertRaises(NonRecoverableError):
                with_nsx_t_client(NSXTResource)(func)()
                func.assert_called()
