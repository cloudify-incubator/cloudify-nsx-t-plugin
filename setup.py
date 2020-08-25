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


from setuptools import setup
from setuptools import find_packages


setup(
    name='cloudify-nsx-t-plugin',
    version='0.3.0',
    author='Cloudify Platform Ltd.',
    author_email='hello@cloudify.co',
    license='LICENSE',
    packages=find_packages(exclude=['tests*']),
    description='A Cloudify plugin for NSX-T',
    install_requires=[
        'cloudify-common>=4.5',
        'vapi-common==2.14.0',
        'vapi-common-client==2.14.0',
        'vapi-runtime==2.14.0',
        'nsx-global-policy-python-sdk==3.0.0.0.0.15946039',
        'nsx-policy-python-sdk==3.0.0.0.0.15946039',
        'nsx-python-sdk==3.0.0.0.0.15946039',
        'IPy==0.81'
    ]
)
