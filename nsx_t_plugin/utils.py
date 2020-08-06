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

from cloudify.exceptions import NonRecoverableError
from cloudify.constants import NODE_INSTANCE, RELATIONSHIP_INSTANCE


def get_relationship_subject_context(_ctx):
    """
    This method is to decide where to get node from relationship context
    since this is not exposed correctly from cloudify
    :param _ctx: current cloudify context object
    :return: RelationshipSubjectContext instance
    """
    # Get the node_id for the current node in order to decide if that node
    # is source | target
    node_id = _ctx._context.get('node_id')

    source_node_id = _ctx.source._context.get('node_id')
    target_node_id = _ctx.target._context.get('node_id')

    if node_id == source_node_id:
        return _ctx.source
    elif node_id == target_node_id:
        return _ctx.target
    else:
        raise NonRecoverableError(
            'Unable to decide if current node is source or target')


def get_ctx_object(_ctx):
    """
    This method is to lookup right context which could be one of
    the following:
     1- Context for source relationship instance
     2- Context for target relationship instance
     3- Current Cloudify Context
    :param _ctx: current cloudify context object
    :return: This could be RelationshipSubjectContext or CloudifyContext
    instance
    """
    if _ctx.type == RELATIONSHIP_INSTANCE:
        return get_relationship_subject_context(_ctx)
    if _ctx.type != NODE_INSTANCE:
        _ctx.logger.warn(
            'CloudifyContext is neither {0} nor {1} type. '
            'Falling back to {0}. This indicates a problem.'.format(
                NODE_INSTANCE, RELATIONSHIP_INSTANCE))
    return _ctx


def populate_nsx_t_instance_from_ctx(class_decl, _ctx, kwargs):
    """
    Prepare an instance for nsx-t so that we can invoke it for later on
    operations like create, delete, get, update and list
    :param class_decl: The class implementation of nsx-t client which is
    subtype of `nsx_t_sdk.common.NSXTResource`
    :param _ctx: Instance of the current context which could be
    RelationshipSubjectContext or CloudifyContext
    :param kwargs: Extra kwargs
    :return: instance of the class_decl ready for use
    """
    def _lookup_property_by_name(property_name):
        property_value = None
        if _ctx.node.properties.get(property_name):
            property_value = \
                _ctx.node.properties.get(property_name)

        if kwargs.get(property_name):
            kwargs_value = kwargs.pop(property_name)
            if isinstance(property_value, dict):
                property_value.update(kwargs_value)
            else:
                return kwargs_value
        return property_value
    client_config = _lookup_property_by_name('client_config')
    resource_config = _lookup_property_by_name('resource_config')

    # Check if resource_id is part of runtime properties so that we
    # can add it to the resource_config
    if 'id' in _ctx.instance.runtime_properties:
        resource_config['id'] = \
            _ctx.instance.runtime_properties['id']

    resource = class_decl(client_config=client_config,
                          resource_config=resource_config,
                          logger=_ctx.logger)

    return resource
