# Copyright 2013 Nicira, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
from oslo_utils import importutils

import nova.network

security_group_opts = [
    cfg.StrOpt(
        'security_group_api',
        default='nova',
        help='DEPRECATED: The full class name of the security API class',
        deprecated_for_removal=True),
]

CONF = cfg.CONF
CONF.register_opts(security_group_opts)

NOVA_DRIVER = ('nova.compute.api.SecurityGroupAPI')
NEUTRON_DRIVER = ('nova.network.security_group.neutron_driver.'
                  'SecurityGroupAPI')
DRIVER_CACHE = {}


def _get_openstack_security_group_driver(skip_policy_check=False):
    if is_neutron_security_groups():
        return importutils.import_object(NEUTRON_DRIVER,
                                         skip_policy_check=skip_policy_check)
    elif CONF.security_group_api.lower() == 'nova':
        return importutils.import_object(NOVA_DRIVER,
                                         skip_policy_check=skip_policy_check)
    else:
        return importutils.import_object(CONF.security_group_api,
                                         skip_policy_check=skip_policy_check)


def get_openstack_security_group_driver(skip_policy_check=False):
    if skip_policy_check not in DRIVER_CACHE:
        DRIVER_CACHE[skip_policy_check] = _get_openstack_security_group_driver(
            skip_policy_check)
    return DRIVER_CACHE[skip_policy_check]


def is_neutron_security_groups():
    return (CONF.security_group_api.lower() == 'neutron'
            or nova.network.is_neutron())
