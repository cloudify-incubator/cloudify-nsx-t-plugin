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


@with_nsx_t_client(Segment)
def create(nsx_t_resource):
    # Update the subnet configuration for segment
    _update_subnet_configuration(nsx_t_resource.resource_config)
    # Trigger the actual call to the NSXT Manager API
    resource = nsx_t_resource.create()
    # Update the resource_id with the new "id" returned from API
    nsx_t_resource.resource_id = resource.id


@with_nsx_t_client(SegmentState)
def start(nsx_t_resource):
    validate_if_resource_started('Segment', nsx_t_resource)


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
