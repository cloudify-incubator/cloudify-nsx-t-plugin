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

from nsx_t_plugin.decorators import with_nsx_t_client
from nsx_t_sdk.resources import DhcpServerConfig, Tier1


@with_nsx_t_client(DhcpServerConfig)
def create(nsx_t_resource):
    resource = nsx_t_resource.create()

    # Update the resource_id with the new "id" returned from API
    nsx_t_resource.resource_id = resource.id

    # Save path as runtime property to use it later on
    ctx.instance.runtime_properties['path'] = resource.path


@with_nsx_t_client(DhcpServerConfig)
def configure(nsx_t_resource):
    tier1_gateway_id = ctx.node.properties.get('tier1_gateway_id')
    if tier1_gateway_id:
        tier1 = Tier1(
            client_config=nsx_t_resource.nsx_t_resource,
            resource_config={
                'id': tier1_gateway_id
            },
            logger=ctx.logger
        )
        tier1_object = tier1.get()
        tier1_object.dhcp_config_paths = [
            ctx.instance.runtime_properties['path']
        ]
        tier1.patch(tier1_object)


@with_nsx_t_client(DhcpServerConfig)
def delete(nsx_t_resource):
    nsx_t_resource.delete()
