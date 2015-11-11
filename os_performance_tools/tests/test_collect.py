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
test_collect
----------------------------------

Tests for `os_performance_tools.collect`
"""

import json
import mock
import tempfile

from os_performance_tools import collect
from os_performance_tools.tests import base
import six
import subunit
import testtools


class StreamResult(testtools.StreamResult):
    counters_content = None

    def status(self, test_id=None, test_status=None, test_tags=None,
               runnable=True, file_name=None, file_bytes=None, eof=False,
               mime_type=None, route_code=None, timestamp=None):
        if test_id:
            return
        if file_name != 'counters.json':
            return
        self.counters_content = file_bytes


class TestCollect(base.TestCase):

    def setUp(self):
        super(TestCollect, self).setUp()
        self.stdout = six.BytesIO()
        self.attachments = []

    @mock.patch('os_performance_tools.collectors.mysql.collect')
    @mock.patch('os_performance_tools.collectors.queues.collect')
    def test_collect_main(self, queues_mock, mysql_mock):
        mysql_mock.return_value = {}
        queues_mock.return_value = {}
        collect.main(['os-collect-counters'], self.stdout)
        content = json.loads(self.stdout.getvalue().decode('utf-8'))
        self.assertTrue(isinstance(content, dict))
        self.assertIn('mysql', content)
        self.assertIn('queues', content)

    def _parse_outcome(self, test):
        self.attachments = {}
        for name, detail in test['details'].items():
            name = name.split(':')[0]
            self.attachments[name] = detail

    @mock.patch('os_performance_tools.collectors.mysql.collect')
    @mock.patch('os_performance_tools.collectors.queues.collect')
    def test_collect_main_subunit(self, queues_mock, mysql_mock):
        mysql_mock.return_value = {}
        queues_mock.return_value = {}
        collect.main(['os-collect-counters', '--subunit'], self.stdout)
        self.stdout.seek(0)
        stream = subunit.ByteStreamToStreamResult(self.stdout)
        result = StreamResult()
        result.startTestRun()
        try:
            stream.run(result)
        finally:
            result.stopTestRun()
        self.assertIsNotNone(result.counters_content)
        content = json.loads(result.counters_content.decode('utf-8'))
        self.assertTrue(isinstance(content, dict))
        self.assertIn('mysql', content)
        self.assertIn('queues', content)

    @mock.patch('os_performance_tools.collectors.mysql.collect')
    @mock.patch('os_performance_tools.collectors.queues.collect')
    def test_collect_main_subunit_and_json(self, queues_mock, mysql_mock):
        mysql_mock.return_value = {}
        queues_mock.return_value = {}
        with tempfile.NamedTemporaryFile() as tfile:
            collect.main(
                ['os-collect-counters', '--subunit', '--output', tfile.name],
                self.stdout)
            content = json.loads(tfile.read().decode('utf-8'))
            self.assertTrue(isinstance(content, dict))
            self.assertIn('mysql', content)
            self.assertIn('queues', content)
        self.stdout.seek(0)
        stream = subunit.ByteStreamToStreamResult(self.stdout)
        result = StreamResult()
        result.startTestRun()
        try:
            stream.run(result)
        finally:
            result.stopTestRun()
        self.assertIsNotNone(result.counters_content)
        content = json.loads(result.counters_content.decode('utf-8'))
        self.assertTrue(isinstance(content, dict))
        self.assertIn('mysql', content)
        self.assertIn('queues', content)
