import json
import os
import re

from subscribe import provider, tool

__DATA_DIR = None


def set_data_dir(data_dir: str):
    global __DATA_DIR
    __DATA_DIR = data_dir


def __get_dir_of_token(token: str) -> str:
    return f'{__DATA_DIR}/tokens/{token}'


def __load_config_of_token(token: str) -> dict:
    fp = f'{__get_dir_of_token(token)}/config.json'
    if not os.path.exists(fp):
        return {}

    with open(f'{__get_dir_of_token(token)}/config.json', 'r') as f:
        return json.load(f)


def gen_config(token: str) -> dict:
    token_config = __load_config_of_token(token)
    if not token_config:
        return {}

    nodes = provider.load_nodes(token_config['providers'])

    config_template = __load_config_template(token, token_config['config_template'])

    return __render_config(config_template, nodes)


def __load_config_template(token: str, conf: dict) -> dict:
    if conf['type'] == 'remote':
        content = tool.http_get_content(conf['download_url'])
        if not content:
            return {}
        return json.loads(content)

    elif conf['type'] == 'local':
        file_path = conf['local_file_path']
        # check if file_path is absolute path
        if not file_path.startswith('/'):
            file_path = f'{__get_dir_of_token(token)}/{file_path}'
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r') as f:
            return json.load(f)

    return {}


def __render_config(config_template: dict, nodes: list[dict]) -> dict:
    outbounds = config_template.get('outbounds', [])

    for outbound in outbounds:
        if outbound['type'] not in {'selector', 'urltest'}:
            continue

        group_outbounds = outbound['outbounds']

        new_group_outbounds = []
        for tag in group_outbounds:
            tag = tag.strip()
            if tag.startswith('{') and tag.endswith('}'):
                # filter nodes
                pattern = tag[1:-1]
                for node in nodes:
                    if re.search(pattern, node['tag']):
                        new_group_outbounds.append(node['tag'])
            else:
                new_group_outbounds.append(tag)

        outbound['outbounds'] = new_group_outbounds

    outbounds.extend(nodes)
    return config_template
