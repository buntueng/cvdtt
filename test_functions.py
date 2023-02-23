import mysql.connector
from pathlib import Path
import logging
import yaml
from yaml import SafeLoader

current_path = Path(__file__).resolve().parents[0]
logging_file_path = Path(current_path, 'template.log')
yml_config_path = Path(current_path, 'config.yml')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

fileHandler = logging.FileHandler(filename=logging_file_path)
fileHandler.setFormatter(logging_format)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging_format)
logger.addHandler(consoleHandler)

def read_yml(file_path):
    yml_params = None
    if file_path.is_file():
        with open(file_path,'r') as yml_file:
            yml_params = yaml.load(yml_file, Loader=SafeLoader)
    else:
        logging.warning("file path is not here")
    return yml_params

configuration_params =read_yml(yml_config_path)

server_host = configuration_params['server_detail']['address']
server_port = configuration_params['server_detail']['port']
database_name = configuration_params['server_detail']['database']
user_account = configuration_params['admin_login']['username']
user_password = configuration_params['admin_login']['password']

try:
    main_db = mysql.connector.connect(  host = server_host,
                                        port = int(server_port),
                                        database = database_name,
                                        user = user_account,
                                        password = user_password,
                                        connection_timeout=2)
    if (main_db):
        logging.debug("server ok")
    else:
        logging.debug("can not connect server")
except:
    logging.debug("Error")
