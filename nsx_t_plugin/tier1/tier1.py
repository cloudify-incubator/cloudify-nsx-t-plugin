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

from nsx_t_plugin.decorators import with_nsx_t_client
from nsx_t_plugin.utils import (
    validate_if_resource_started,
    validate_if_resource_deleted
)
from nsx_t_sdk.resources import Tier1, Tier1state


@with_nsx_t_client(Tier1)
def create(nsx_t_resource):
    # Trigger the actual call to the NSXT Manager API
    resource = nsx_t_resource.create()
    # Update the resource_id with the new "id" returned from API
    nsx_t_resource.resource_id = resource.id


@with_nsx_t_client(Tier1state)
def start(nsx_t_resource):
    validate_if_resource_started(nsx_t_resource)


@with_nsx_t_client(Tier1)
def delete(nsx_t_resource):
    validate_if_resource_deleted(nsx_t_resource)
