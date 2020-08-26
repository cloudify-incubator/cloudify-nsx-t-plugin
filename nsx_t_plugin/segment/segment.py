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

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError

from nsx_t_plugin.decorators import with_nsx_t_client
from nsx_t_plugin.constants import (
    STATE_IN_PROGRESS,
    STATE_SUCCESS,
    STATE_PENDING,
)
from nsx_t_plugin.utils import (
    validate_if_resource_started,
    validate_if_resource_deleted
)
from nsx_t_sdk.resources import (
    Segment,
    SegmentState,
    SegmentPort
)


def _update_subnet_configuration(resource_config):
    subnet = resource_config.pop('subnet', {})
    if subnet:
        resource_config['subnets'] = []
        for ip_option in ['ip_v4_config', 'ip_v6_config']:
            ip_option_config = subnet.get(ip_option)
            if ip_option_config:
                resource_config['subnets'].append(ip_option_config)


def _get_networks_info_from_inputs(network_unique_id, ip_address):
    if not network_unique_id:
        network_unique_id = ctx.target.instance.runtime_properties.get(
            'unique_id'
        )
    if not ip_address:
        raise NonRecoverableError(
            '`ip_address` is a required input and must be provided'
        )
    server_networks = ctx.source.instance.runtime_properties.get('networks')
    server_id = ctx.source.instance.runtime_properties.get('id')
    if not server_id:
        server_id = ctx.source.instance.id
    if not server_networks:
        raise NonRecoverableError(
            '`networks` runtime property is either not set or empty for '
            'server {0}'.format(server_id))
    return network_unique_id, server_networks


@with_nsx_t_client(Segment)
def create(nsx_t_resource):
    # Update the subnet configuration for segment
    _update_subnet_configuration(nsx_t_resource.resource_config)
    # Trigger the actual call to the NSXT Manager API
    resource = nsx_t_resource.create()
    # Update the resource_id with the new "id" returned from API
    nsx_t_resource.resource_id = resource.id

    # Set the unique_id to use it later on
    ctx.instance.runtime_properties['unique_id'] = resource.unique_id


@with_nsx_t_client(SegmentState)
def start(nsx_t_resource):
    validate_if_resource_started(
        'Segment',
        nsx_t_resource,
        [STATE_PENDING, STATE_IN_PROGRESS],
        [STATE_SUCCESS]
    )


@with_nsx_t_client(Segment)
def stop(nsx_t_resource):
    segment_port = SegmentPort(
        client_config=nsx_t_resource.client_config,
        logger=ctx.logger,
        resource_config={}
    )
    for nsx_t_port in segment_port.list(
            filters={
                'segment_id': nsx_t_resource.resource_id
            }
    ):
        port = SegmentPort(
            client_config=nsx_t_resource.client_config,
            logger=ctx.logger,
            resource_config={'id': nsx_t_port['id']}
        )
        port.delete((nsx_t_resource.resource_id,))


@with_nsx_t_client(Segment)
def delete(nsx_t_resource):
    validate_if_resource_deleted(nsx_t_resource)


@with_nsx_t_client(Segment)
def add_static_bindings(nsx_t_resource, network_unique_id, ip_address):
    network_unique_id, networks = _get_networks_info_from_inputs(
        network_unique_id, ip_address
    )
    for network in networks:
        if network.get('name') == 'network_unique_id':
            mac_address = network.get('mac')
            break
    else:
        raise NonRecoverableError(
            'Network {0} is not attached to server. Select a valid '
            'network'.format(network_unique_id)
        )

    if not mac_address:
        raise NonRecoverableError(
            'Mac address cannot be empty '
            'for network {0}'.format(network_unique_id)
        )

    segment = nsx_t_resource.get(to_dict=False)
    segment.address_bindings = [
        {
            'ip_address': ip_address,
            'mac_address': mac_address
        }
    ]
    segment = nsx_t_resource.update(segment)
    ctx.target.instance.runtime_properties['resource_config'] = segment.to_dict
