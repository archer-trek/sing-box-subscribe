
import argparse
import json

from api import app
from subscribe import config


def build_parser():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(dest='__command__')

    server_cmd = sub_parser.add_parser('server')
    server_cmd.add_argument('-d', '--data-dir', type=str, default='data')

    gen_cmd = sub_parser.add_parser('gen')
    gen_cmd.add_argument('-d', '--data-dir', type=str, default='data')
    gen_cmd.add_argument('-t', '--token', type=str)
    gen_cmd.add_argument('-o', '--output', type=str, default='config.json')

    return parser


if __name__ == '__main__':
    from logging.config import dictConfig

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    parser = build_parser()
    args = parser.parse_args()

    cmd = args.__command__
    if cmd == 'server':
        config.set_data_dir(args.data_dir)
        app.run()
    elif cmd == 'gen':
        config.set_data_dir(args.data_dir)
        conf = config.gen_config(args.token)
        with open(args.output, 'w') as f:
            json.dump(conf, f, indent=2, ensure_ascii=False)
