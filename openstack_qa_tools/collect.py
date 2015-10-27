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

import argparse
import json
import logging
import threading

from openstack_qa_tools.collectors import mysql
from openstack_qa_tools.collectors import queues

mysql_data = {}
queues_data = {}


def get_mysql():
    global mysql_data
    mysql_data = mysql.collect()


def get_queues():
    global queues_data
    queues_data = queues.collect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', default=logging.INFO)
    args = parser.parse_args()
    logging.basicConfig(
        format='%(asctime)-15s %(levelname)s %(threadName)s: %(message)s')
    log = logging.getLogger()
    log.setLevel(args.loglevel)
    getmysql = threading.Thread(name='mysql', target=get_mysql)
    getqueues = threading.Thread(name='queues', target=get_queues)
    getmysql.start()
    getqueues.start()
    log.debug('waiting for threads')

    getmysql.join()
    getqueues.join()
    log.debug('threads all returned')

    final = {
        'mysql': mysql_data,
        'queues': queues_data,
    }

    print(json.dumps(final, indent=1))

if __name__ == '__main__':
    main()
