"""
Usage:
    ACG-KillTransactionLogger <instance>
    ACG-KillTransactionLogger ( -h | --version)

Positional Arguments:
    <instance>      Config instance name

Options:
    --list          List running threads
    --kill <ID>     ID of Thread to kill
    -h              Show this screen
    --version       Show Version Information
© 2022 Application Consulting Group
"""
from TM1py import TM1Service
from TM1py.Exceptions import TM1pyException, TM1pyNotAdminException
from docopt import docopt

from utilities import get_tm1_config

APP_NAME = 'ACG-KillTransactionLogger'
APP_VERSION = '2.0'
APP_MSG = '© 2022 Application Consulting Group'
FILE = ''


def main(instance: str) -> None:
    try:
        config = get_tm1_config(instance=instance)
        config['session_context'] = 'ACG-ThreadKill'
        with TM1Service(**config) as tm1:
            threads = tm1.monitoring.get_threads()
            for thread in threads:
                if thread['Context'] == 'ACG-GetTransactions':
                    tm1.monitoring.cancel_thread(thread['ID'])
    except TM1pyNotAdminException:
        print("TM1 Admin permissions required")
    except TM1pyException as t:
        t_msg = str(t).split('-')
        if t_msg[2].strip() == "Reason:L Unauthorized":
            print("Login failure, check credentials")
        else:
            print(str(t))


if __name__ == '__main__':
    cmd_args = docopt(__doc__, version=f"{APP_NAME}, Version: {APP_VERSION} \n {APP_MSG}")
    _instance = cmd_args.get("<instance>")
    main(instance=_instance)
