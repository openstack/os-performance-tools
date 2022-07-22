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
#
# This file was forked from dstat's mysql5_innodb plugin but retains none of
# that original code other than a list of well known MySQL variable names.
''' MySQL is accessed via the configuration options found at ~/.my.cnf. This is
parsed not by libmysqlclient, which may or may not be present, but by
configparser. As such, some options that are usually usable from that file may
be ignored by this module. Everything from the "client" section will be passed
through to pymysql's connect method.
'''

import configparser
import logging
import os

import pymysql

from os_performance_tools import error

COLLECT_COUNTERS = (
    'Com_delete',
    'Com_insert',
    'Com_select',
    'Com_update',
    'Connections',
    'Innodb_buffer_pool_read_requests',
    'Innodb_data_reads',
    'Innodb_data_read',
    'Innodb_data_writes',
    'Innodb_data_written',
    'Innodb_log_writes',
    'Innodb_rows_deleted',
    'Innodb_rows_inserted',
    'Innodb_rows_read',
    'Innodb_rows_updated',
    'Queries',
    'Slow_queries',
)
'''These counters' meaning are all documented in the `MySQL manual
<http://dev.mysql.com/doc/refman/5.6/en/server-status-variables.html>`_.
They are intended to show a picture of how much has been asked of
MySQL, and how busy MySQL was while executing commands. Each one will
be recorded unaltered by name in the resulting counters mapping.
'''


def _get_config():
    args = {}
    try:
        with open(os.path.expanduser("~/.my.cnf")) as dfile:
            parser = configparser.ConfigParser()
            parser.read_file(dfile)
            for k, v in parser.items('client'):
                args[k] = v
    except IOError as e:
        raise error.CollectionError(str(e))
    return args


def collect():
    log = logging.getLogger()
    args = _get_config()
    conn = pymysql.connect(**args)
    cursor = conn.cursor()
    counters = {}
    cursor.execute('show global status')
    while True:
        result = cursor.fetchone()
        if result is None:
            break
        k, v = result
        if k in COLLECT_COUNTERS:
            counters[k] = int(v)
    log.debug(counters)
    return counters
