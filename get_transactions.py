"""
Usage:
    ACG-GetTransactions <instance> <cube> <since> <location> <timeout>
    ACG-GetTransactions (-h | --version)

Positional Arguments:
    <instance>      Config instance name
    <cube>          Cube name to retrieve
    <since>         Timestamp of first entry to retrieve
    <location>      Location to place output file
    <timeout>       Timeout in seconds

Options:
    -h              Show this screen
    --version       Show Version Information

© Copyright 2022 Application Consulting Group
"""
import os
import threading
import time
from datetime import datetime

import pandas as pd
from TM1py import TM1Service
from TM1py.Exceptions import TM1pyException, TM1pyNotAdminException
from docopt import docopt

from baselogger import logger, APP_NAME
from utilities import get_tm1_config

APP_VERSION = '5.1'


def main(_config: dict, cube: str, since: datetime, output: str, thread_event):
    _file = os.path.join(output, cube + '.csv')
    try:
        with TM1Service(**_config) as tm1:
            tm1.server.get_server_name()
            entries = tm1.server.get_transaction_log_entries(cube=cube, since=since)
        df = pd.DataFrame(entries)
        if len(df) > 0:
            df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
            df.sort_values(by='TimeStamp', inplace=True, ascending=True)
            df.to_csv(_file, index=False)
            return 1
        else:
            logger.error(f"No transactions for '{cube}' found for {since}")
            return None
    except TM1pyException as t:
        t_msg = str(t).split('-')
        if (t_msg[2]).strip() == "Reason: 'Unauthorized'":
            logger.error('Login failure, check non-interactive user credentials')
            return None
        else:
            logger.error(t)
            return None
    except TM1pyNotAdminException:
        logger.error('Administrative permissions required')
        return None


def term_thread(_config: dict):
    _config['session_context'] = 'ACG-ThreadKill'
    with TM1Service(**_config) as tm1:
        threads = tm1.monitoring.get_threads()
        for thread in threads:
            if thread['Context'] == 'ACG-GetTransactions':
                tm1.monitoring.cancel_thread(thread['ID'])


if __name__ == '__main__':
    start = time.perf_counter()
    cmd_args = docopt(__doc__, version=f"{APP_NAME}, Version: {APP_VERSION}"
                                       f"\n© Copyright 2022 Application Consulting Group")
    logger.info(fr"Starting {APP_NAME}:  Searching transactions for '{cmd_args['<cube>']}', storing file '{cmd_args['<location>']}\{cmd_args['<cube>']}.csv', " 
                fr"since '{cmd_args['<since>']}'")
    _instance = cmd_args.get('<instance>')
    _cube = cmd_args.get('<cube>')
    _since_time = cmd_args.get('<since>')
    # Parse date field and convert to date object
    year = int(_since_time[0:4])
    month = int(_since_time[5:7])
    day = int(_since_time[8:10])
    hour = int(_since_time[11:13])
    minute = int(_since_time[14:16])
    second = int(_since_time[17:19])
    since_time = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    path = cmd_args.get("<location>")
    _timeout = int(cmd_args.get("<timeout>"))
    config = get_tm1_config(instance=_instance)
    thread_event = threading.Event()
    thread_event.clear()
    t = threading.Thread(target=main, name="Main", args=(config, _cube, since_time, path, thread_event))
    t.start()
    thread_event.wait(timeout=_timeout)
    if t.is_alive():
        logger.error(f"Hit timeout {_timeout} seconds, killing thread")
        thread_event.set()
        term_thread(config)
    end = time.perf_counter()
    logger.info(f"Finished process in {round(end - start, 2)} seconds")
