# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from oslo_config import cfg
import statsd

OPTS_GROUP = cfg.OptGroup(name='counters2statsd', title='Counters2Statsd')

OPTS = [
    cfg.StrOpt('host', help='Statsd host to connect to', default=None),
    cfg.IntOpt('port', help='Port on statsd host to connect to', default=None),
    cfg.StrOpt('prefix', help='Prefix to add to stats', default=None),
]

_statsd_client = None


def get_statsd_client():
    global _statsd_client
    if _statsd_client is None:
        cfg.CONF.register_group(OPTS_GROUP)
        cfg.CONF.register_opts(OPTS, group=OPTS_GROUP)
        _statsd_client = statsd.StatsClient(cfg.CONF.counters2statsd.host,
                                            cfg.CONF.counters2statsd.port,
                                            cfg.CONF.counters2statsd.prefix)
    return _statsd_client


def add_test_run_attachments(attachments, test_run_id, session):
    for attachment in attachments:
        try:
            counters = json.loads(attachment)
        except ValueError:
            continue
        if not isinstance(counters, dict):
            continue
        if '__counters_meta__' not in counters:
            continue
        client = get_statsd_client()
        for groupname, values in counters.items():
            if not isinstance(values, dict):
                continue
            for k, v in values.items():
                k = '{}.{}'.format(groupname, k)
                try:
                    v = int(v)
                except ValueError:
                    continue
                client.incr(k, v)
