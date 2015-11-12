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

import tempfile

import json
from oslo_config import cfg
try:
    import statsd
except ImportError:
    statsd = None
import testtools

OPTS_GROUP = cfg.OptGroup(name='counters2statsd', title='Counters2Statsd')

OPTS = [
    cfg.StrOpt('host', help='Statsd host to connect to', default='localhost'),
    cfg.IntOpt('port', help='Port on statsd host to connect to', default=8125),
    cfg.StrOpt('prefix', help='Prefix to add to stats', default=None),
    cfg.BoolOpt('enabled', help='Set to false to disable this plugin',
                default=True)
]

_statsd_client = None


class Pipeline(object):
    '''Wrapper for statsd.Pipeline

    statsd's API doesn't say if prefix can be changed on the fly so
    we're going to assume it cannot be and make a wrapper that does that.
    '''
    def __init__(self, pipeline, dynamic_prefix=None):
        self.pipeline = pipeline
        self.dynamic_prefix = dynamic_prefix

    def _add_dynamic_prefix(self, call, *args, **kwargs):
        if args:
            args = list(args)
            stat = args.pop(0)
        elif 'stat' in kwargs:
            stat = kwargs.pop('stat')
        else:
            return call(*args, **kwargs)
        if self.dynamic_prefix:
            stat = '{}.{}'.format(self.dynamic_prefix, stat)
        call(stat, *args, **kwargs)

    def incr(self, *args, **kwargs):
        return self._add_dynamic_prefix(self.pipeline.incr, *args, **kwargs)

    def timing(self, *args, **kwargs):
        return self._add_dynamic_prefix(self.pipeline.timing, *args, **kwargs)

    def send(self):
        return self.pipeline.send()


def get_statsd_client():
    global _statsd_client
    if _statsd_client is None:
        _statsd_client = statsd.StatsClient(cfg.CONF.counters2statsd.host,
                                            cfg.CONF.counters2statsd.port,
                                            cfg.CONF.counters2statsd.prefix)
        _statsd_client = Pipeline(_statsd_client.pipeline())
    return _statsd_client


class AttachmentResult(testtools.StreamResult):
    """Keeps track of top level results with StreamToDict drops.

    We use a SpooledTemporaryFile to keep it performant with smaller files
    but to ensure we don't use up tons of RAM. Anything over 1MB will be
    spooled out to disk.
    """
    @classmethod
    def enabled(cls):
        cfg.CONF.register_group(OPTS_GROUP)
        cfg.CONF.register_opts(OPTS, group=OPTS_GROUP)
        cfg.CONF.register_cli_opts(OPTS, group=OPTS_GROUP)
        return bool(statsd)

    def __init__(self):
        super(AttachmentResult, self).__init__()
        self.attachments = {}

    def status(self, test_id=None, test_status=None, test_tags=None,
               runnable=True, file_name=None, file_bytes=None, eof=False,
               mime_type=None, route_code=None, timestamp=None):
        if not cfg.CONF.counters2statsd.enabled:
            return
        if test_id is not None:
            return
        if not file_name:
            return
        if file_name not in self.attachments:
            self.attachments[file_name] = tempfile.SpooledTemporaryFile(
                max_size=2 ** 30)
        self.attachments[file_name].write(file_bytes)
        if eof:
            self.attachments[file_name].seek(0)

    def stopTestRun(self):
        if not cfg.CONF.counters2statsd.enabled:
            return
        client = get_statsd_client()
        for file_name, attachment in self.attachments.items():
            if file_name != 'counters.json':
                continue
            try:
                try:
                    attachment.seek(0)
                    counters = json.loads(attachment.read().decode('utf-8'))
                except AttributeError:
                    counters = json.loads(attachment)
            except ValueError:
                continue
            if not isinstance(counters, dict):
                continue
            client.dynamic_prefix = counters.get('__meta__', {}).get('prefix')
            for groupname, values in counters.items():
                if not isinstance(values, dict):
                    continue
                if groupname == '__meta__':
                    if 'delta_seconds' in values:
                        client.timing(
                            'testrun', values['delta_seconds'] * 1000)
                    continue
                for k, v in values.items():
                    k = '{}.{}'.format(groupname, k)
                    try:
                        v = int(v)
                    except ValueError:
                        continue
                    client.incr(k, v)
        client.send()
