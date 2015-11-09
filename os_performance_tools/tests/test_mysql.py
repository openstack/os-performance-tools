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

import mock

from os_performance_tools.collectors import mysql
from os_performance_tools.tests import base


class TestOpenStackQaTools(base.TestCase):

    @mock.patch('os_performance_tools.collectors.mysql._get_config')
    @mock.patch('pymysql.connect')
    def test_mysql(self, pymysql_mock, get_config_mock):
        connection = mock.MagicMock()
        curs = mock.MagicMock()
        side_effect = [(k, 0) for k in mysql.COLLECT_COUNTERS]
        side_effect.append(None)  # Instead of StopIteration pymsql uses None
        curs.fetchone.side_effect = side_effect
        connection.cursor.return_value = curs
        pymysql_mock.return_value = connection
        result = mysql.collect()
        self.assertEqual(sorted(mysql.COLLECT_COUNTERS),
                         sorted(result.keys()))
        self.assertTrue(all([val == 0 for val in result.values()]))
