import logging
import os
import pprint

import boto3


def set_logger(log_level: str = "INFO") -> object:
    log_level = os.environ.get("LOG_LEVEL", log_level).strip().upper()
    logging.basicConfig(format="[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    return logger


logger = set_logger()


def set_pretty_printer():
    return pprint.PrettyPrinter(indent=2, width=100)


def get_tavily_api(key: str, region_name: str) -> str:

    if not os.path.isfile("../.env"):
        raise Exception('Local environment variable file .env not existing! Please create with the command: cp .env.tmp .env')
    
    tavily_api_prefix = "tvly-"
    if not os.environ[key].startswith(tavily_api_prefix):
        logger.info(f"{key} value not correctly set in the .env file, expected a key to start with \"{tavily_api_prefix}\" but got it starting with \"{os.environ[key][:5]}\". Trying from AWS Secrets Manager.")
        session = boto3.session.Session()
        secrets_manager = session.client(service_name="secretsmanager", region_name=region_name)
        try:
            secret_value = secrets_manager.get_secret_value(SecretId=key)
        except Exception as e:
            logger.error(f"{key} secret couldn't be retrieved correctly from AWS Secrets Manager either! Received error message:\n{e}")
            raise e

        logger.info(f"{key} variable correctly retrieved from the AWS Secret Manager.")
        secret_string = secret_value["SecretString"]
        secret = eval(secret_string, {"__builtins__": {}}, {})[key]
        if not secret:
            raise Exception(f"{key} value not correctly set in the AWS Secrets Manager, expected a key to start with \"{tavily_api_prefix}\" but got it starting with \"{os.environ[key][:5]}\".")
        os.environ[key] = secret
    else:
        logger.info(f"{key} variable correctly retrieved from the .env file.")
        secret = os.environ[key]

    return secret
