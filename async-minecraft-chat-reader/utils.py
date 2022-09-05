import logging

import configargparse


def get_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    return logger


def parse_args() -> configargparse.Namespace:
    parser = configargparse.ArgParser(default_config_files=[".txt"])
    parser.add_argument(
        "--send_host",
        env_var="SEND_HOST",
        help="host for minecraft server",
    )
    parser.add_argument(
        "--send_port",
        env_var="PORT",
        type=int,
        help="port for minecraft server",
    )
    parser.add_argument("-t", "--token", env_var="TOKEN", help="Username token")
    parser.add_argument("-u", "--username", env_var="USERNAME", help="Your username")

    parser.add_argument(
        "--listener_host",
        env_var="LISTENER_HOST",
        help="host for minecraft server",
    )
    parser.add_argument(
        "--listener_port",
        env_var="LISTENER_PORT",
        type=int,
        help="port for minecraft server",
    )
    parser.add_argument(
        "-f",
        "--file-path",
        env_var="FILE_PATH",
        help="file path for chat logs",
    )

    return parser.parse_args()
