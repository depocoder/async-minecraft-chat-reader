import configargparse


def parse_args() -> configargparse.Namespace:
    parser = configargparse.ArgParser(default_config_files=['.env'])
    parser.add_argument('-p', '--port', type=int, env_var='PORT', required=True, help='port for minecraft server')
    parser.add_argument('-hs', '--host', env_var='HOST', required=True, help='host for minecraft server')
    parser.add_argument('-f', '--file-path', env_var='FILE_PATH', help='file path for logs')
    parser.add_argument('-t', '--token', env_var='TOKEN', help='Username token')
    parser.add_argument('-u', '--username', env_var='USERNAME', help='Your username')
    return parser.parse_args()
