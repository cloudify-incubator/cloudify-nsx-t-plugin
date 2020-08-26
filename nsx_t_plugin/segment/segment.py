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
    SegmentPort,
    DhcpV4StaticBindingConfig,
    DhcpV6StaticBindingConfig
)


def _update_subnet_configuration(resource_config):
    subnet = resource_config.pop('subnet', {})
    if subnet:
        resource_config['subnets'] = []
        for ip_option in ['ip_v4_config', 'ip_v6_config']:
            ip_option_config = subnet.get(ip_option)
            if ip_option_config:
                resource_config['subnets'].append(ip_option_config)


def _get_networks_info_from_inputs(
        network_unique_id,
        ip_v4_address,
        ip_v6_address
):
    if not network_unique_id:
        network_unique_id = ctx.target.instance.runtime_properties.get(
            'unique_id'
        )
    if not any([ip_v4_address, ip_v6_address]):
        raise NonRecoverableError(
            '`ip_v4_address` & `ip_v6_address` cannot be both unset, '
            'select at least on of them'
        )
    server_networks = ctx.source.inst_ance.runtime_properties.get('networks')
    server_id = ctx.source.instance.runtime_properties.get('id')
    if not server_id:
        server_id = ctx.source.instance.id
    if not server_networks:
        raise NonRecoverableError(
            '`networks` runtime property is either not set or empty for '
            'server {0}'.format(server_id))
    return network_unique_id, server_networks


def _prepare_dhcp_static_binding_configs(
        segment_id,
        mac_address,
        ipv4_address,
        ip_v6_address
):
    dhcp_v4_config = {}
    dhcp_v6_config = {}

    if ipv4_address:
        dhcp_v4_config['id'] = '{segment}-{dhcp}'.format(
            segment=segment_id, dhcp='dhcpv4'
        )
        dhcp_v4_config['ip_address'] = ipv4_address
        dhcp_v4_config['mac_address'] = mac_address

    if ip_v6_address:
        dhcp_v6_config['id'] = '{segment}-{dhcp}'.format(
            segment=segment_id, dhcp='dhcpv6'
        )
        dhcp_v6_config['ip_addresses'] = [ip_v6_address]
        dhcp_v6_config['mac_address'] = mac_address

    return dhcp_v4_config, dhcp_v6_config


def _create_dhcp_static_binding_configs(
        segment_id,
        client_config,
        dhcp_v4_config,
        dhcp_v6_config
):
    if dhcp_v4_config:
        dhcp_v4_binding = DhcpV4StaticBindingConfig(
            client_config=client_config,
            logger=ctx.logger,
            resource_config=dhcp_v4_config)
        dhcp_v4_static_binding_id = dhcp_v4_config.pop('id')
        dhcp_v4_binding_response = dhcp_v4_binding.update(
            segment_id,
            dhcp_v4_static_binding_id,
            dhcp_v4_config
        )
        ctx.target.instance.runtime_properties['dhcp_v4_static_binding_id'] = \
            dhcp_v4_static_binding_id
        ctx.target.instance.runtime_properties['dhcp_v4_static_binding'] = \
            dhcp_v4_binding_response

    if dhcp_v6_config:
        dhcp_v6_binding = DhcpV6StaticBindingConfig(
            client_config=client_config,
            logger=ctx.logger,
            resource_config=dhcp_v6_config)
        dhcp_v6_static_binding_id = dhcp_v6_config.pop('id')
        dhcp_v6_binding_response = dhcp_v6_binding.update(
            segment_id,
            dhcp_v6_static_binding_id,
            dhcp_v6_config
        )
        ctx.target.instance.runtime_properties['dhcp_v6_static_binding_id'] = \
            dhcp_v6_static_binding_id
        ctx.target.instance.runtime_properties['dhcp_v6_static_binding'] = \
            dhcp_v6_binding_response


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
        port.delete(nsx_t_resource.resource_id, nsx_t_port['id'])


@with_nsx_t_client(Segment)
def delete(nsx_t_resource):
    validate_if_resource_deleted(nsx_t_resource)


@with_nsx_t_client(Segment)
def add_static_bindings(
        nsx_t_resource,
        network_unique_id,
        ip_v4_address,
        ip_v6_address
):
    network_unique_id, networks = _get_networks_info_from_inputs(
        network_unique_id, ip_v4_address, ip_v6_address
    )
    for network in networks:
        if network.get('name') == network_unique_id:
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
    dhcp_v4_config, dhcp_v6_config = _prepare_dhcp_static_binding_configs(
        nsx_t_resource.id,
        mac_address,
        ip_v4_address,
        ip_v6_address
    )
    _create_dhcp_static_binding_configs(
        nsx_t_resource.id,
        nsx_t_resource.client_config,
        dhcp_v4_config,
        dhcp_v6_config
    )


@with_nsx_t_client(Segment)
def remove_static_bindings(nsx_t_resource):
    dhcp_v4_static_binding_id = ctx.target.instance.runtime_properties.get(
        'dhcp_v4_static_binding_id'
    )
    dhcp_v6_static_binding_id = ctx.target.instance.runtime_properties.get(
        'dhcp_v6_static_binding_id'
    )
    if not any([dhcp_v4_static_binding_id, dhcp_v6_static_binding_id]):
        raise NonRecoverableError(
            'DHCP Static binding ids are not set for '
            'ipv4 & ipv6, at least one must be set as '
            'runtime property'
        )
    if dhcp_v4_static_binding_id:
        dhcp_v4_binding = DhcpV4StaticBindingConfig(
            client_config=nsx_t_resource.client_config,
            resource_config={'id': dhcp_v4_static_binding_id},
            logger=ctx.logger
        )
        dhcp_v4_binding.delete(nsx_t_resource.id, dhcp_v4_static_binding_id)

    if dhcp_v6_static_binding_id:
        dhcp_v6_binding = DhcpV6StaticBindingConfig(
            client_config=nsx_t_resource.client_config,
            resource_config={'id': dhcp_v6_static_binding_id},
            logger=ctx.logger
        )
        dhcp_v6_binding.delete(nsx_t_resource.id, dhcp_v6_static_binding_id)
