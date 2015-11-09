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
test_collectors
----------------------------------

Tests for `os_performance_tools.collectors`
"""

import json
import mock

from os_performance_tools.collectors import queues
from os_performance_tools.tests import base


class TestOpenStackQaTols(base.TestCase):

    @mock.patch('six.moves.http_client.HTTPConnection')
    def test_queues(self, httplib_mock):
        reader = mock.MagicMock(name='getresponse_reader')
        rval = json.dumps([{'name': 'foo', 'message_stats': {'publish': 1}}])
        reader.read.return_value = rval
        conn = httplib_mock.return_value
        conn.getresponse.return_value = reader
        data = queues.collect()
        self.assertEqual({'foo_publish': 1}, data)
