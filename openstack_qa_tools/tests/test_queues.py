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

Tests for `openstack_qa_tools.collectors`
"""

import mock

from openstack_qa_tools.collectors import queues
from openstack_qa_tools.tests import base


class TestOpenStackQaTols(base.TestCase):

    @mock.patch('six.moves.http_client.HTTPConnection')
    def test_queues(self, httplib_mock):
        reader = mock.MagicMock(name='getresponse_reader')
        reader.read.return_value = '[]'
        conn = httplib_mock.return_value
        conn.getresponse.return_value = reader
        data = queues.collect()
        self.assertEqual({}, data)
