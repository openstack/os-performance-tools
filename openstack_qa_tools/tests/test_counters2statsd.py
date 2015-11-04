# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_counters2statsd
----------------------------------

Tests for `openstack_qa_tools.counters2statsd`
"""

import json
import mock

from openstack_qa_tools import counters2statsd
from openstack_qa_tools.tests import base


class TestOpenStackQaTols(base.TestCase):

    @mock.patch('statsd.StatsClient')
    def test_add_test_run_attachments(self, statsd_mock):
        mock_client = mock.MagicMock('statsd_client')
        mock_client.incr = mock.MagicMock('statds_incr')
        statsd_mock.return_value = mock_client
        fake_counters = {'mysql': {'Queries': 10}}
        fake_counters['__counters_meta__'] = {}
        fake_counters = json.dumps(fake_counters)
        counters2statsd.add_test_run_attachments([fake_counters], 'foo', None)
        statsd_mock.assert_called_with(None, None, None)
        mock_client.incr.assert_called_with('mysql.Queries', 10)
