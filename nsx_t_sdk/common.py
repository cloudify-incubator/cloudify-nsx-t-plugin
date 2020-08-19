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

import requests

from vmware.vapi.lib import connect
from vmware.vapi.security import user_password
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.bindings.error import VapiError

from com.vmware import nsx_policy_client
from com.vmware import nsx_client
from com.vmware.nsx_policy import infra_client
from com.vmware.nsx_policy.infra import segments_client

from nsx_t_sdk import exceptions
from nsx_t_sdk._compat import text_type

AUTH_SESSION = 'session'
AUTH_BASIC = 'basic'

ACTION_CREATE = 'create'
ACTION_UPDATE = 'update'
ACTION_PATCH = 'patch'
ACTION_DELETE = 'delete'
ACTION_GET = 'get'
ACTION_LIST = 'list'


class NSXTResource(object):
    client_type = False

    resource_type = None
    service_name = None

    allow_create = True
    allow_delete = True
    allow_get = True
    allow_list = True
    allow_update = True
    allow_patch = True

    def __init__(self, client_config, resource_config, logger):
        self.client_config = client_config
        self.logger = logger
        self.resource_config = resource_config or {}
        self.resource_config['resource_type'] = self.resource_type
        self.resource_id = self.resource_config.pop('id', None)
        self._api_client = self._prepare_nsx_t_client()

    @staticmethod
    def _get_nsx_client_map():
        return {
            'nsx': nsx_client,
            'nsx_policy': nsx_policy_client,
            'nsx_infra': infra_client,
            'segment': segments_client
        }

    def _get_stub_factory_for_nsx_client(self, stub_config):
        client = self._get_nsx_client_map()[self.client_type]
        return client.StubFactory(stub_config)

    @property
    def username(self):
        return self.client_config.get('username')

    @property
    def password(self):
        return self.client_config.get('password')

    @property
    def host(self):
        return self.client_config.get('host')

    @property
    def port(self):
        return self.client_config.get('port')

    @property
    def auth_type(self):
        return self.client_config.get('auth_type')

    @property
    def cert(self):
        return self.client_config.get('cert')

    @property
    def insecure(self):
        return self.client_config.get('insecure')

    @property
    def url(self):
        return 'https://{0}:{1}'.format(self.host, self.port)

    def _prepare_session_auth(self, session):
        self.logger.debug('Prepare session authentication....')
        resp = session.post(
            '{0}/{1}'.format(self.url, 'api/session/create'),
            data={
                'j_username': self.username,
                'j_password': self.password
            }
        )
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        session.headers['Cookie'] = resp.headers.get('Set-Cookie')
        session.headers['X-XSRF-TOKEN'] = resp.headers.get('X-XSRF-TOKEN')
        self.logger.debug('Session Cookie & X-XSRF-TOKEN are set successfully')

    def _prepare_nsx_t_client(self):
        session = requests.session()
        session.verify = self.insecure
        session.cert = self.cert
        # Only Relevant for auth session
        if self.auth_type == AUTH_SESSION:
            self.logger.debug('API calls is using session authentication')
            self._prepare_session_auth(session)

        connector = connect.get_requests_connector(
            session=session,
            msg_protocol='rest',
            url=self.url
        )
        stub_config = StubConfigurationFactory.new_runtime_configuration(
            connector,
            response_extractor=True
        )
        # Only relevant for basic auth
        if self.auth_type == AUTH_BASIC:
            self.logger.debug('API calls is using basic authentication')
            security_context = \
                user_password.create_user_password_security_context(
                    self.username,
                    self.password
                )
            connector.set_security_context(security_context)
        stub_factory = self._get_stub_factory_for_nsx_client(stub_config)
        return ApiClient(stub_factory)

    def _invoke(self, action, args=None, kwargs=None):
        args = args or ()
        kwargs = kwargs or {}
        self.logger.debug('HTTP Request Args: {0}'.format(args))
        self.logger.debug('HTTP Request Kwargs: {0}'.format(kwargs))
        service_client = getattr(self._api_client, self.service_name)
        service_action = getattr(service_client, action)
        try:
            if args and kwargs:
                result = service_action(*args, **kwargs)
            elif args:
                result = service_action(*args)
            elif kwargs:
                result = service_action(**kwargs)
            else:
                result = service_action()
        except VapiError as error:
            raise exceptions.NSXTSDKException(text_type(error))

        self.logger.debug(
            'API Request Result: {0} '
            'for invoking action {1}'
            ' using service {2}'
            ''.format(result, action, self.resource_type))
        return result

    def _validate_allowed_method(self, allowed_action, action):
        if not allowed_action:
            raise exceptions.MethodNotAllowed(
                'Not allowed to invoke {0} '
                'method for {1}'.format(action, self.resource_type)
            )

    def create(self):
        return self.update(self.resource_config)

    def update(self, new_config=None):
        self._validate_allowed_method(self.allow_update, ACTION_UPDATE)
        return self._invoke(
            ACTION_UPDATE,
            (self.resource_id, new_config,),
        )

    def patch(self, new_config=None):
        self._validate_allowed_method(self.allow_patch, ACTION_PATCH)
        return self._invoke(
            ACTION_PATCH,
            (self.resource_id, new_config,),
        )

    def delete(self, extra_params=None):
        extra_params = extra_params or ()
        self._validate_allowed_method(self.allow_delete, ACTION_DELETE)
        params = (self.resource_id,)
        if extra_params:
            params += extra_params

        return self._invoke(ACTION_DELETE, params)

    def get(self):
        self._validate_allowed_method(self.allow_get, ACTION_GET)
        return self._invoke(ACTION_GET, (self.resource_id,))

    def list(self,
             cursor=None,
             included_fields=None,
             page_size=None,
             sort_ascending=None,
             sort_by=None,
             filters=None):
        self._validate_allowed_method(self.allow_list, ACTION_LIST)
        params = {
            'cursor': cursor,
            'included_fields': included_fields,
            'page_size': page_size,
            'sort_ascending': sort_ascending,
            'sort_by': sort_by,
        }
        if filters:
            params.update(filters)
        results = self._invoke(ACTION_LIST, kwargs=params).to_dict()
        return results['results'] if results.get('results') else []
