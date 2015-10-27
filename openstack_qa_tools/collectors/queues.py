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

import base64
import json
import logging
import os
import socket

from six.moves import http_client

from openstack_qa_tools import error

DSTAT_RABBITMQ_API = os.environ.get('DSTAT_RABBITMQ_API',
                                    '127.0.0.1:15672')
DSTAT_RABBITMQ_API_USER = os.environ.get('DSTAT_RABBITMQ_USER',
                                         'guest')
DSTAT_RABBITMQ_API_PASS = os.environ.get('DSTAT_RABBITMQ_PASS',
                                         'guest')


def collect():
    log = logging.getLogger()
    conn = http_client.HTTPConnection(DSTAT_RABBITMQ_API)
    auth = '%s:%s' % (DSTAT_RABBITMQ_API_USER, DSTAT_RABBITMQ_API_PASS)
    auth = base64.encodestring(auth.encode('utf-8')).decode('ascii')
    auth = auth.replace('\n', '')
    auth = {'Authorization': 'Basic %s' % auth}
    try:
        conn.request('GET', '/api/queues', headers=auth)
        log.debug('requested /api/queues')
        content = conn.getresponse().read()
        log.debug('received content [%s]' % content)
    except (socket.error, http_client.HTTPException) as e:
        raise error.CollectionError(str(e))

    content = json.loads(content)
    if not isinstance(content, list):
        raise error.CollectionError(
            'Unexpected format encountered. %s' % content)
    collected = {}
    for q in content:
        if not isinstance(q, dict):
            continue
        if "name" not in q or "messages" not in q:
            continue
        qname = q["name"]
        if "message_stats" in q and "publish" in q["message_stats"]:
            target = '%s_message_stats' % (qname)
            collected[target] = q["message_stats"]["publish"]
    return collected
