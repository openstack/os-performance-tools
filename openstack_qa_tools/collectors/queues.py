# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import base64
import httplib
import json
import os
import socket
import urllib2

from openstack_qa_tools import error

DSTAT_RABBITMQ_API = os.environ.get('DSTAT_RABBITMQ_API',
                                    '127.0.0.1:15672')
DSTAT_RABBITMQ_API_USER = os.environ.get('DSTAT_RABBITMQ_USER',
                                    'guest')
DSTAT_RABBITMQ_API_PASS = os.environ.get('DSTAT_RABBITMQ_PASS',
                                    'guest')

def collect():
    conn = httplib.HTTPConnection(DSTAT_RABBITMQ_API)
    auth = base64.encodestring('%s:%s' % (DSTAT_RABBITMQ_API_USER,
                                               DSTAT_RABBITMQ_API_PASS))
    auth = auth.replace('\n', '')
    auth = {'Authorization': 'Basic %s' % auth}
    try:
        conn.request('GET', '/api/queues', headers=auth)
        content = conn.getresponse().read()
    except (socket.error, httplib.HTTPException) as e:
        raise error.CollectionError(str(e))

    content = json.loads(content)
    if not isinstance(content, list):
        raise error.CollectionError('Unexpected format encountered. %s' % content)
    collected = {}
    for q in content:
        if not isinstance(q, dict):
            continue
        if "name" not in q or "messages" not in q:
            continue
        qname = q["name"]
        if "message_stats" in q and "publish" in q["message_stats"]:
            newpub = q["message_stats"]["publish"]
            target = '%s_message_stats' % (qname)
            collected[target] = q["message_stats"]["publish"]
    return collected
