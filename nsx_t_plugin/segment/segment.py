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
from cloudify.exceptions import OperationRetry, NonRecoverableError

from nsx_t_plugin.decorators import with_nsx_t_client
from nsx_t_sdk.resources import (
    Segment,
    SegmentState,
    SegmentPort
)
from nsx_t_sdk.exceptions import NSXTSDKException

SEGMENT_TASK_DELETE = 'segment_delete_task'
SEGMENT_STATE_PENDING = 'pending'
SEGMENT_STATE_IN_PROGRESS = 'in_progress'
SEGMENT_STATE_SUCCESS = 'success'


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
    segment_state = nsx_t_resource.get()
    state = segment_state.state
    if state in [SEGMENT_STATE_PENDING, SEGMENT_STATE_IN_PROGRESS]:
        raise OperationRetry(
            'Segment state '
            'is still in {0} state'.format(state)
        )
    elif state == SEGMENT_STATE_SUCCESS:
        ctx.logger.info('Segment started successfully')
    else:
        raise NonRecoverableError(
            'Segment failed to started {0}'.format(state)
        )


@with_nsx_t_client(Segment)
def stop(nsx_t_resource):
    port = SegmentPort(
        client_config=nsx_t_resource.client_config,
        logger=ctx.logger,
        resource_config={}
    )

    try:
        port.list(filters={'segment_id': nsx_t_resource.resource_id})
    except NSXTSDKException:
        ctx.logger.info(
            'No more ports attached'
            ' to segment: {0}'.format(nsx_t_resource.resource_id)
        )
        return
    else:
        raise OperationRetry(
            message='Segment {0} still has port attached to it.'
                    ''.format(nsx_t_resource.resource_id)
        )


@with_nsx_t_client(Segment)
def delete(nsx_t_resource):
    try:
        nsx_t_resource.get()
    except NSXTSDKException:
        ctx.logger.info('Segment {0} is deleted successfully'
                        .format(nsx_t_resource.resource_id))
        return

    if SEGMENT_TASK_DELETE not in ctx.instance.runtime_properties:
        nsx_t_resource.delete()
        ctx.instance.runtime_properties[SEGMENT_TASK_DELETE] = True

    ctx.logger.info(
        'Waiting for segment "{0}" to be deleted'.format(
            nsx_t_resource.resource_id,
        )
    )
    raise OperationRetry(
        message='Segment {0} not deleted yet.'
                ''.format(nsx_t_resource.resource_id)
    )
