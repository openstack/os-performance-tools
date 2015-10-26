### Author: HIROSE Masaaki <hirose31 _at_ gmail.com>

import os

import pymysql
from six.moves import configparser

from openstack_qa_tools import error

COLLECT_COUNTERS = (
    'Com_delete',
    'Com_insert',
    'Com_select',
    'Com_update',
    'Connections',
    'Innodb_buffer_pool_read_requests',
    'Innodb_data_reads',
    'Innodb_data_writes',
    'Innodb_log_writes',
    'Innodb_rows_deleted',
    'Innodb_rows_inserted',
    'Innodb_rows_read',
    'Innodb_rows_updated',
    'Queries',
    'Slow_queries',
    'Threads_connected',
    'Threads_running',
)


def _get_config():
    args = {}
    try:
        with open(os.path.expanduser("~/.my.cnf")) as dfile:
            parser = configparser.ConfigParser()
            parser.readfp(dfile)
            for k,v in parser.items('client'):
                args[k] = v
    except IOError as e:
        raise error.CollectionError(str(e))
    return args


def collect():
    args = _get_config()
    conn = pymysql.connect(**args)
    cursor = conn.cursor()
    counters = {}
    while True:
        cursor.execute('show global status')
        result = cursor.fetchone()
        if result is None:
            break
        k, v = result
        if k in COLLECT_COUNTERS:
            counters[k] = int(v)
    return counters
