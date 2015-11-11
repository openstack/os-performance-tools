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
test_delta
----------------------------------

Tests for `os_performance_tools.collectors._delta`
"""

import testscenarios

from os_performance_tools.collectors import _delta
from os_performance_tools.tests import base


class TestOSQATDelta(testscenarios.WithScenarios, base.TestCase):

    scenarios = [
        ('add1', dict(
            previous={'zoo': {'aardvark': 9, 'zebra': 0}},
            current={'zoo': {'aardvark': 12, 'zebra': 0}},
            expected={'zoo': {'aardvark': 3, 'zebra': 0}})),
        ('newkey', dict(
            previous={'zoo': {'bee': 0}},
            current={'lake': {'trout': 1}, 'zoo': {'bee': 5}},
            expected={'lake': {'trout': 1}, 'zoo': {'bee': 5}})),
        ('delkey', dict(
            previous={'zoo': {'cat': 99}},
            current={},
            expected={})),
        ('newvar', dict(
            previous={'zoo': {'dog': 9}},
            current={'zoo': {'dog': 9, 'ocelot': 2}},
            expected={'zoo': {'dog': 0, 'ocelot': 2}})),
        ('delvar', dict(
            previous={'zoo': {'elephant': 1000, 'bear': 1}},
            current={'zoo': {'elephant': 1000}},
            expected={'zoo': {'elephant': 0}})),
        ('stringval', dict(
            previous={'zoo': 'foo'},
            current={'zoo': 0},
            expected=ValueError)),
        ('newstrval', dict(
            previous={'zoo': {'giraffe': 100}},
            current={'zoo': {'giraffe': 'tall'}},
            expected=ValueError)),
        ('changetype', dict(
            previous={'zoo': {'horse': 7}},
            current={'zoo': 15},
            expected=ValueError)),
        ('meta_unixtime', dict(
            previous={'__meta__': {'unixtime': 1.0}},
            current={'__meta__': {'unixtime': 10.5}},
            expected={'__meta__': {'unixtime': 10.5, 'delta_seconds': 9.5}})),
        ('meta_unixtime_gone', dict(
            previous={'__meta__': {'unixtime': 1.0}},
            current={},
            expected={})),
        ('meta_unixtime_new', dict(
            previous={},
            current={'__meta__': {'unixtime': 1.0}},
            expected={'__meta__': {'unixtime': 1.0}})),
    ]

    def test_delta(self):
        if self.expected is ValueError:
            self.assertRaises(ValueError, _delta.delta, self.previous,
                              self.current)
        else:
            self.assertEqual(self.expected, _delta.delta(self.previous,
                                                         self.current))
