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

from IPy import IP

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError, OperationRetry

from nsx_t_plugin.decorators import with_nsx_t_client
from nsx_t_sdk.resources import (
     VirtualMachine,
     VirtualNetworkInterface,
     SegmentPort
)


def _update_network_with_ipv4_and_ipv6(network):
    ipv_4 = []
    ipv_6 = []
    ip_address_info = network.get('ip_address_info', []) or []
    for ip_address_obj in ip_address_info:
        ip_addresses = ip_address_obj.get('ip_addresses', []) or []
        for ip_address in ip_addresses:
            if IP(ip_address).version() == 4:
                ipv_4.append(ip_address)
            elif IP(ip_address).version() == 6:
                ipv_6.append(ip_address)

    network['ipv4_addresses'] = ipv_4
    network['ipv6_addresses'] = ipv_6


def _lookup_segment_ports(client_config, network_name):
    segment_port = SegmentPort(
        client_config=client_config,
        logger=ctx.logger,
        resource_config={}
    )
    ports = []
    for nsx_t_port in segment_port.list(
            filters={
                'segment_id': network_name
            }
    ):
        if nsx_t_port.get('attachment'):
            ports.append(nsx_t_port['attachment']['id'])

    return ports


def _get_target_network(ports, network):
    if not network.get('lport_attachment_id'):
        return {}
    return network if network['lport_attachment_id'] in ports else {}


def _populate_networks_for_virtual_machine(
        client_config,
        owner_vm_id,
        network_id,
        networks
):
    ports = _lookup_segment_ports(client_config, network_id)
    if not ports:
        raise OperationRetry(
            'Network {0} is still not connected to any device'.format(
                network_id))
    else:
        networks_obj = {}
        networks_obj['networks'] = {}
        target_network = {}
        for network in networks:
            _update_network_with_ipv4_and_ipv6(network)
            if not target_network:
                target_network = _get_target_network(ports, network)
            networks_obj['networks'][network['display_name']] = network

        if not target_network:
            raise NonRecoverableError(
                'The selected network {0} is not '
                'attached to target virtual machine {1}'
                ''.format(network_id, owner_vm_id)
            )

        ctx.instance.runtime_properties[network_id] = target_network
        ctx.instance.runtime_properties['networks'] = networks_obj


@with_nsx_t_client(VirtualMachine)
def create(nsx_t_resource):
    network_id = nsx_t_resource.resource_config.get('network_id')
    if not network_id:
        raise NonRecoverableError(
            'Network name is required in order '
            'to fetch the network interface attached to target '
            'virtual machine'
        )
    ctx.logger.info(
        'Preparing resource to fetch target network interface'
        ' {0} for target virtual machine'
        ''.format(network_id)
    )


@with_nsx_t_client(VirtualNetworkInterface)
def configure(nsx_t_resource):
    owner_vm_id = ctx.instance.runtime_properties.get('id')
    if not owner_vm_id:
        owner_vm_id = nsx_t_resource.resource_id
    filters = {
        'owner_vm_id': owner_vm_id
    }
    # This will list all networks interface attached to specific vm
    networks = nsx_t_resource.list(filters=filters)
    network_id = nsx_t_resource.resource_config.get('network_id')
    if not networks:
        raise NonRecoverableError(
            'Virtual Machine is not attached to any '
            'network'
        )
    _populate_networks_for_virtual_machine(
        nsx_t_resource.client_config,
        owner_vm_id,
        network_id,
        networks
    )
