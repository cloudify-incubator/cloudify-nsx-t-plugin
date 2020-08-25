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
from nsx_t_sdk.resources import VirtualMachine, VirtualNetworkInterface


@with_nsx_t_client(VirtualMachine)
def create(nsx_t_resource):
    network_name = nsx_t_resource.resource_config.get('network_name')
    if not network_name:
        raise NonRecoverableError(
            'Network name is required in order '
            'to fetch the network interface attached to target '
            'virtual machine'
        )
    ctx.logger.info(
        'Preparing resource to fetch target network interface'
        ' {0} for target virtual machine'
        ''.format(network_name)
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
    network_name = nsx_t_resource.resource_config.get('network_name')
    if not networks:
        raise NonRecoverableError(
            'Virtual Machine is not attached to any '
            'network'
        )
    networks_obj = {}
    networks_obj['networks'] = {}
    for network in networks:
        networks_obj['networks'][network['display_name']] = network

    if networks_obj['networks'].get(network_name):
        ctx.instance.runtime_properties[network_name] = networks_obj[
            'networks'][network_name]
    else:
        raise NonRecoverableError(
            'The selected network {0} is not '
            'attached to target virtual machine {1}'
            ''.format(network_name, owner_vm_id)
        )
    ctx.instance.runtime_properties['networks'] = networks_obj
