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

import json


def delta(previous, current, meta=False):
    product = {}
    seen = set()

    # Old keys
    for k, v in previous.items():
        if k not in current:
            continue
        newv = current[k]
        if type(v) is not type(newv):
            raise ValueError(
                'Type of key %s changed from %s to %s' % (k,
                                                          type(v),
                                                          type(newv)))
        if k == '__meta__':
            meta = True
        if meta and k == 'delta_seconds':
            continue
        elif meta and k == 'unixtime':
            product['delta_seconds'] = newv - v
            product[k] = newv
        elif isinstance(v, int) or isinstance(v, float):
            product[k] = newv - v
        elif isinstance(v, dict):
            product[k] = delta(v, newv, meta)
        else:
            raise ValueError('Only mappings of numbers are understood')
        seen.add(k)
    # New keys
    for k in set(current.keys()) - seen:
        product[k] = current[k]
    return product


def delta_with_file(previous_path, current_data):
    with open(previous_path) as previous_file:
        previous_data = json.loads(previous_file.read())
    return delta(previous_data, current_data)
