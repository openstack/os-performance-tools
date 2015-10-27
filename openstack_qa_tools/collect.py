import json
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
    getmysql = threading.Thread(name='mysql', target=get_mysql)
    getqueues = threading.Thread(name='queues', target=get_queues)
    getmysql.start()
    getqueues.start()

    getmysql.join()
    getqueues.join()

    final = {
        'mysql': mysql_data,
        'queues': queues_data,
    }

    print(json.dumps(final, indent=1))

if __name__ == '__main__':
    main()
