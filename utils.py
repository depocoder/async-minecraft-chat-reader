import configargparse


def create_main_parser():
    parser = configargparse.ArgParser(default_config_files=['.env'])
    parser.add_argument('-p', '--port', type=int, required=True, help='port for minecraft server')
    parser.add_argument('-hs', '--host', required=True, help='host for minecraft server')
    return parser


def parse_sender_args() -> configargparse.Namespace:
    parser = create_main_parser()
    parser.add_argument('-t', '--token', env_var='TOKEN', help='Username token')
    parser.add_argument('-u', '--username', env_var='USERNAME', help='Your username')
    return parser.parse_args()


def parse_chat_listener_args() -> configargparse.Namespace:
    parser = create_main_parser()
    parser.add_argument('-f', '--file-path', env_var='FILE_PATH', help='file path for chat logs')
    return parser.parse_args()
