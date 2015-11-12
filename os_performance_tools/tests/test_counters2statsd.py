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
import time

from os_performance_tools import counters2statsd
from os_performance_tools.tests import base


class TestCounters2Statsd(base.TestCase):

    @mock.patch('statsd.StatsClient')
    def test_add_test_run_attachments(self, statsd_mock):
        mock_client = mock.MagicMock('statsd_client')
        statsd_mock.return_value = mock_client
        mock_client.pipeline = mock.MagicMock('statsd_pipeline')
        mock_pipeline = mock.MagicMock('Pipeline')
        mock_pipeline.incr = mock.MagicMock('statds_incr')
        mock_pipeline.send = mock.MagicMock('statds_send')
        mock_client.pipeline.return_value = mock_pipeline
        fake_counters = {'mysql': {'Queries': 10}}
        fake_counters = json.dumps(fake_counters).encode('utf-8')
        self.assertTrue(counters2statsd.AttachmentResult.enabled())
        result = counters2statsd.AttachmentResult()
        result.status(file_name='counters.json', file_bytes=fake_counters)
        result.stopTestRun()
        statsd_mock.assert_called_with('localhost', 8125, None)
        mock_pipeline.incr.assert_called_with('mysql.Queries', 10)
        mock_pipeline.send.assert_called_with()

    @mock.patch('statsd.StatsClient')
    def test_add_test_run_attachments_meta(self, statsd_mock):
        mock_client = mock.MagicMock('statsd_client')
        statsd_mock.return_value = mock_client
        mock_client.pipeline = mock.MagicMock('statsd_pipeline')
        mock_pipeline = mock.MagicMock('Pipeline')
        mock_pipeline.incr = mock.MagicMock('statds_incr')
        mock_pipeline.timing = mock.MagicMock('statds_timing')
        mock_pipeline.send = mock.MagicMock('statds_send')
        mock_client.pipeline.return_value = mock_pipeline
        fake_counters = {
            '__meta__': {
                'unixtime': time.time(),
                'delta_seconds': 10.5,
                'prefix': 'all-tests',
            },
            'mysql': {
                'Queries': 50
            }
        }
        fake_counters = json.dumps(fake_counters).encode('utf-8')
        self.assertTrue(counters2statsd.AttachmentResult.enabled())
        result = counters2statsd.AttachmentResult()
        result.status(file_name='counters.json', file_bytes=fake_counters)
        result.stopTestRun()
        statsd_mock.assert_called_with('localhost', 8125, None)
        mock_pipeline.timing.assert_called_with('all-tests.testrun', 10500)
        mock_pipeline.incr.assert_called_with('all-tests.mysql.Queries', 50)
        mock_pipeline.send.assert_called_with()
