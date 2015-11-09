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

Tests for `os_performance_tools.counters2statsd`
"""

import json
import mock

from os_performance_tools import counters2statsd
from os_performance_tools.tests import base


class TestOpenStackQaTols(base.TestCase):

    @mock.patch('statsd.StatsClient')
    def test_add_test_run_attachments(self, statsd_mock):
        mock_client = mock.MagicMock('statsd_client')
        mock_client.incr = mock.MagicMock('statds_incr')
        statsd_mock.return_value = mock_client
        fake_counters = {'mysql': {'Queries': 10}}
        fake_counters = json.dumps(fake_counters).encode('utf-8')
        self.assertTrue(counters2statsd.AttachmentResult.enabled())
        result = counters2statsd.AttachmentResult()
        result.status(file_name='counters.json', file_bytes=fake_counters)
        result.stopTestRun()
        statsd_mock.assert_called_with('localhost', 8125, None)
        mock_client.incr.assert_called_with('mysql.Queries', 10)
