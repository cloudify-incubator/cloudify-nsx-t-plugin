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

# STATE VALUES
STATE_PENDING = 'pending'
STATE_IN_PROGRESS = 'in_progress'
STATE_SUCCESS = 'success'

# SEGMENTS
TASK_DELETE = 'delete_task'

# OPERATIONS
DELETE_OPERATION = 'cloudify.interfaces.lifecycle.delete'
CREATE_OPERATION = 'cloudify.interfaces.lifecycle.create'

# RUNTIME PROPERTIES
BASIC_RUNTIME_PROPERTIES = (
    'id',
    'resource_type'
)
NSXT_ID_PROPERTY = 'id'
NSXT_NAME_PROPERTY = 'name'
NSXT_TYPE_PROPERTY = 'type'
NSXT_RESOURCE_CONFIG_PROPERTY = 'resource_config'