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
import sys
import threading
import time

from os_performance_tools.collectors import _delta
from os_performance_tools.collectors import mysql
from os_performance_tools.collectors import queues
from subunit import v2 as subunit_v2

mysql_data = {}
queues_data = {}


def get_mysql():
    global mysql_data
    mysql_data = mysql.collect()


def get_queues():
    global queues_data
    queues_data = queues.collect()


def main(argv=None, stdout=None):
    if stdout is None:
        stdout = sys.stdout
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(argv[0])
    parser.add_argument('--loglevel', default=logging.INFO)
    parser.add_argument('--delta', help="Path to json file to read previous "
                                        "values from")
    parser.add_argument('--subunit', nargs='?', default=None,
                        const='counters.json',
                        help="Wrap the json output in a subunit stream. If an "
                        "argument is passed used that as the filename, "
                        "otherwise 'counters.json' will be used")
    parser.add_argument('--output', help="Write JSON here. Does not disable "
                        "stdout.")
    parser.add_argument('--meta-prefix', help="Set a prefix in __meta__")
    args = parser.parse_args(argv[1:])
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

    meta = {'unixtime': time.time()}
    if args.meta_prefix:
        meta['prefix'] = args.meta_prefix

    collected = {
        '__meta__': meta,
        'mysql': mysql_data,
        'queues': queues_data,
    }
    if args.delta:
        collected = _delta.delta_with_file(args.delta, collected)
    content = json.dumps(collected, indent=1, sort_keys=True).encode('utf-8')
    if args.subunit is not None:
        file_name = args.subunit or 'counters.json'
        stream = subunit_v2.StreamResultToBytes(stdout)
        stream.startTestRun()
        stream.status(file_name=file_name, file_bytes=content,
                      mime_type='application/json')
        stream.stopTestRun()
    else:
        stdout.write(content)
        stdout.write(b"\n")
    if args.output:
        with open(args.output, 'wb') as output:
            output.write(content)
            output.write(b"\n")

if __name__ == '__main__':
    main()
