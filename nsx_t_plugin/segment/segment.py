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
from cloudify.exceptions import NonRecoverableError, OperationRetry

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
    DhcpV4StaticBindingConfig,
    DhcpV6StaticBindingConfig,
    DhcpStaticBindingState
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
    server_networks = ctx.source.instance.runtime_properties.get('networks')
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


def _handle_dhcp_static_bindings(
        class_type,
        dhcp_type,
        segment_id,
        client_config,
        dhcp_config):
    tasks = ctx.target.instance.runtime_properties.setdefault('tasks', {})
    if dhcp_config:
        dhcp_binding = class_type(
            client_config=client_config,
            logger=ctx.logger,
            resource_config=dhcp_config)
        if not tasks.get(dhcp_config['id']):
            dhcp_binding_response = dhcp_binding.update(
                segment_id,
                dhcp_binding.resource_id,
                dhcp_config
            )
            tasks[dhcp_config['id']] = True
            ctx.target.instance.runtime_properties[
                'dhcp_{0}_static_binding_id'.format(dhcp_type)] = \
                dhcp_binding.resource_id
            ctx.target.instance.runtime_properties[
                'dhcp_{0}_static_binding'.format(dhcp_type)] = \
                dhcp_binding_response.to_dict()
        else:
            static_state = DhcpStaticBindingState(
                client_config=client_config,
                resource_config={},
                logger=ctx.logger
            )

            validate_if_resource_started(
                'DhcpStaticBinding',
                static_state,
                [STATE_PENDING, STATE_IN_PROGRESS],
                [STATE_SUCCESS],
                args=(segment_id, dhcp_binding.resource_id,)
            )


def _create_dhcp_static_binding_configs(
        segment_id,
        client_config,
        dhcp_v4_config,
        dhcp_v6_config
):
    _handle_dhcp_static_bindings(
        DhcpV4StaticBindingConfig,
        'v4',
        segment_id,
        client_config,
        dhcp_v4_config
    )
    _handle_dhcp_static_bindings(
        DhcpV6StaticBindingConfig,
        'v6',
        segment_id,
        client_config,
        dhcp_v6_config
    )


def _wait_on_dhcp_static_bindings(segment_id, client_config):
    dhcp_v4_binding = DhcpV4StaticBindingConfig(
        client_config=client_config,
        resource_config={},
        logger=ctx.logger
    )

    dhcp_v6_binding = DhcpV4StaticBindingConfig(
        client_config=client_config,
        resource_config={},
        logger=ctx.logger
    )

    bindings_v4 = []
    bindings_v6 = []
    for static_v4_bindings in dhcp_v4_binding.list(
            filters={
                'segment_id': segment_id
            }
    ):
        bindings_v4.append(static_v4_bindings['id'])

    for dhcp_v6_binding in dhcp_v6_binding.list(
            filters={
                'segment_id': segment_id
            }
    ):
        bindings_v6.append(dhcp_v6_binding['id'])

    if any([bindings_v4, bindings_v6]):
        raise OperationRetry(
            'There are still some DHCP static binding not removed yet'
        )


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
    _wait_on_dhcp_static_bindings(
        nsx_t_resource.resource_id,
        nsx_t_resource.client_config
    )


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
        nsx_t_resource.resource_id,
        mac_address,
        ip_v4_address,
        ip_v6_address
    )
    _create_dhcp_static_binding_configs(
        nsx_t_resource.resource_id,
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
        dhcp_v4_binding.delete(
            nsx_t_resource.resource_id,
            dhcp_v4_static_binding_id
        )

    if dhcp_v6_static_binding_id:
        dhcp_v6_binding = DhcpV6StaticBindingConfig(
            client_config=nsx_t_resource.client_config,
            resource_config={'id': dhcp_v6_static_binding_id},
            logger=ctx.logger
        )
        dhcp_v6_binding.delete(
            nsx_t_resource.resource_id,
            dhcp_v6_static_binding_id
        )
