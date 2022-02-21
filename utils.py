import logging

import configargparse


def get_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    return logger


def parse_args() -> configargparse.Namespace:
    parser = configargparse.ArgParser(default_config_files=[".env"])
    parser.add_argument("--send_port", env_var="SEND_PORT", type=int, required=True, help="port for minecraft server")
    parser.add_argument("--send_host", env_var="SEND_HOST", required=True, help="host for minecraft server")
    parser.add_argument("-t", "--token", env_var="TOKEN", help="Username token")
    parser.add_argument("-u", "--username", env_var="USERNAME", help="Your username")

    parser.add_argument("--listener_port", env_var="LISTENER_PORT", type=int, required=True, help="port for minecraft server")
    parser.add_argument("--listener_host", env_var="LISTENER_HOST", required=True, help="host for minecraft server")
    parser.add_argument("-f", "--file-path", env_var="FILE_PATH", help="file path for chat logs")

    return parser.parse_args()
