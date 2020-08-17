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
import sys
from functools import wraps

from cloudify.exceptions import NonRecoverableError
from cloudify.utils import exception_to_error_cause
from cloudify import ctx as CloudifyContext

from nsx_t_plugin.utils import (
    get_ctx_object,
    populate_nsx_t_instance_from_ctx,
    update_runtime_properties_for_instance
)


def with_nsx_t_client(class_decl):
    def _decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            _ctx = kwargs.pop('ctx', CloudifyContext)
            _ctx = get_ctx_object(_ctx)
            operation_name = _ctx.operation.name
            kwargs['nsx_t_resource'] = populate_nsx_t_instance_from_ctx(
                class_decl,
                _ctx,
                kwargs
            )
            try:
                func(**kwargs)
            except Exception as error:
                _, _, tb = sys.exc_info()
                raise NonRecoverableError(
                    'Failure while trying to run operation:'
                    '{0}: {1}'.format(operation_name, error),
                    causes=[exception_to_error_cause(error, tb)])
            else:
                update_runtime_properties_for_instance(
                    kwargs['nsx_t_resource'],
                    _ctx,
                    operation_name
                )
        return wrapper
    return _decorator
