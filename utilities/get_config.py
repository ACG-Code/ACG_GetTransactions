from utilities import DB, PySecrets
from configparser import ConfigParser
from baselogger import application_path, APP_NAME
from getpass import getpass
import os

FILE = os.path.join(application_path, "config.ini")


def str_to_bool(arg: str) -> bool:
    return arg.lower() in ['y', 'yes', 't', 'true', '1', 'on']


def get_tm1_config(instance: str) -> dict:
    """
    Read in config.ini, attach username and password
    :param instance: TM1 Section name from config file
    :return: dict of values needed for TM1PY
    """
    _user = None
    _pass = None
    base_url = None
    address = None
    port = None
    gateway = None
    namespace = None
    ssl = False
    config = ConfigParser()
    config.read(FILE)
    if config.has_section(instance):
        _cloud = str_to_bool(config[instance]['cloud'])
        if _cloud:
            base_url = config[instance]['address']
        else:
            address = config[instance]['address']
            ssl = config[instance]['ssl']
            port = config[instance]['port']
            gateway = config[instance]['gateway']
            namespace = config[instance]['namespace']
        db = DB()
        secrets = PySecrets()
        results = db.retrieve_secrets(secret=instance)
        for result in results:
            _user = result.username
            _pass = result.password
        username = secrets.make_public(secret=_user)
        password = secrets.make_public(secret=_pass)
        if _cloud:
            _config = {
                'address': base_url,
                'user': username,
                'password': password,
                'namespace': 'LDAP',
                'ssl': True,
                'verify': True,
                'async_requests_mode': True
            }
        else:
            _config = {
                'address': address,
                'port': port,
                'ssl': ssl,
                'gateway': gateway,
                'namespace': namespace,
                'user': username,
                'password': password
            }
        _config['session_context'] = APP_NAME
    else:
        _config = create_section(instance=instance, config=config)
    return _config


def print_error(area: str) -> None:
    print(f"{area} is required")


def create_section(instance: str, config: ConfigParser) -> dict:
    base_url = None
    address = None
    port = None
    gateway = None
    namespace = None
    ssl = False
    _cloud = str_to_bool(input(f"Is the '{instance}' on IBM Cloud (default=False): "))
    if _cloud:
        while True:
            base_url = input(f"Enter base url for '{instance}': ")
            if not base_url:
                print_error(area="base_url")
                continue
            else:
                break
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        while True:
            servername = input(f"Enter server name for '{instance}': ")
            if not servername:
                print_error(area='Server name')
                continue
            else:
                break
        while True:
            username = input(f"Enter Non-Interactive username for '{instance}': ")
            if not username:
                print_error(area="User name")
                continue
            else:
                break
        while True:
            password = getpass(f"Enter password for '{username}': ")
            if not password:
                print_error(area="Password")
            else:
                break
    else:
        while True:
            address = input(f"Enter ADMINHOST address for '{instance}': ")
            if not address:
                print_error(area="Address")
                continue
            else:
                break
        while True:
            port = input(f"Enter HTTPPortNumber from Tm1s.cfg for '{instance}': ")
            if not port:
                print_error(area='HTTPPortNumber')
                continue
            else:
                break
        ssl = str_to_bool(input(f"Does '{instance}' use SSL (default=False): "))
        namespace = input(f"Enter Namespace for '{instance}' (leave blank if no CAM Security): ")
        if not namespace:
            namespace = ''
        gateway = input(f"Enter ClientCAMURL from Tm1s.cfg file for '{instance}' (leave empty if no SSO): ")
        if not gateway:
            gateway = ''
        while True:
            username = input(f"Enter username for '{instance}': ")
            if not username:
                print_error(area="User name")
                continue
            else:
                break
        while True:
            password = getpass(f"Enter password for '{username}': ")
            if not password:
                print_error(area="Password")
                continue
            else:
                break
    db = DB()
    secrets = PySecrets()
    if db.secret_exists(secret=instance):
        db.delete_secret(secret=instance)
    _user = secrets.make_secret(secret=username)
    _pass = secrets.make_secret(secret=password)
    db.create_secrets(secret=instance, username=_user, password=_pass)
    if _cloud:
        _config = {
            'base_url': base_url,
            'user': username,
            'password': password,
            'namespace': 'LDAP',
            'ssl': True,
            'verify': True,
            'async_requests_mode': True
        }
        _conf_inst = {
            'cloud': _cloud,
            'address': base_url
        }
    else:
        _config = {
            'address': address,
            'port': port,
            'ssl': ssl,
            'gateway': gateway,
            'namespace': namespace,
            'user': username,
            'password': password
        }
        _conf_inst = {
            'cloud': False,
            'address': address,
            'port': port,
            'ssl': ssl,
            'gateway': gateway,
            'namespace': namespace
        }
    config[instance] = _conf_inst
    config.write(open(FILE, 'w'))
    _config['session_context'] = APP_NAME
    return _config
