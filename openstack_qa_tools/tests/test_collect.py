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

Tests for `openstack_qa_tools.collect`
"""

import functools
import json
import mock

import fixtures
from openstack_qa_tools import collect
from openstack_qa_tools.tests import base
import six
import subunit
import testtools
from testtools import content as ttc


class TestCollect(base.TestCase):

    def setUp(self):
        super(TestCollect, self).setUp()
        self.stdout = six.BytesIO()
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.stdout))
        self.attachments = []

    @mock.patch('openstack_qa_tools.collectors.mysql.collect')
    @mock.patch('openstack_qa_tools.collectors.queues.collect')
    def test_collect_main(self, queues_mock, mysql_mock):
        mysql_mock.return_value = {}
        queues_mock.return_value = {}
        collect.main(['os-collect-counters'])
        content = json.loads(self.stdout.getvalue())
        self.assertTrue(isinstance(content, dict))
        self.assertIn('mysql', content)
        self.assertIn('queues', content)

    def _parse_outcome(self, test):
        self.attachments = {}
        for name, detail in test['details'].items():
            name = name.split(':')[0]
            self.attachments[name] = detail

    @mock.patch('openstack_qa_tools.collectors.mysql.collect')
    @mock.patch('openstack_qa_tools.collectors.queues.collect')
    def test_collect_main_subunit(self, queues_mock, mysql_mock):
        mysql_mock.return_value = {}
        queues_mock.return_value = {}
        collect.main(['os-collect-counters', '--subunit'])
        self.stdout.seek(0)
        stream = subunit.ByteStreamToStreamResult(self.stdout)
        starts = testtools.StreamResult()
        summary = testtools.StreamSummary()
        outcomes = testtools.StreamToDict(
            functools.partial(self._parse_outcome))
        result = testtools.CopyStreamResult([starts, outcomes, summary])
        result.startTestRun()
        try:
            stream.run(result)
        finally:
            result.stopTestRun()
        self.assertIn('counters.json', self.attachments)
        content = json.loads(self.attachments['counters.json'])
        self.assertTrue(isinstance(content, dict))
        self.assertIn('mysql', content)
        self.assertIn('queues', content)
