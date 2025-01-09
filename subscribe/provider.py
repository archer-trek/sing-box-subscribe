"""
provider format:

{
    "tag": "World",
    "type": "remote",
    "download_url": "",
    "download_interval": "2h",
    "download_ua": "clash.meta",
    "excludes": "新疆专用|0网站",
    "exclude_protocols": [
        "shadowsocks"
    ],
    "outbound_override": {
        "tag_prefix": "",
        "tag_suffix": ""
    }
}
"""
import logging
import re

import yaml

import parsers
from subscribe import tool
from subscribe.clash2base64 import clash2v2ray


def load_nodes(providers: list[dict]) -> list[dict]:
    nodes = []
    for provider in providers:
        nodes.extend(__load_nodes(provider))
    return nodes


def __load_nodes(provider: dict) -> list[dict]:
    content = tool.http_get_content(provider['download_url'], provider.get('download_ua'))
    if not content:
        logging.error('load nodes from %s failed', provider['download_url'])
        return []

    raw_proxies = None
    if 'proxies' in content:
        # maybe it's clash yaml config
        config = yaml.safe_load(content)
        raw_proxies = [clash2v2ray(p) for p in config['proxies']]
    else:
        raw_proxies = content.splitlines()

    nodes = __parse_proxies(raw_proxies)
    nodes = __filter_nodes(nodes, provider.get('excludes'), provider.get('exclude_protocols'))
    nodes = __rename_nodes(nodes, provider.get('outbound_override'))
    return nodes


def __filter_nodes(nodes: list[dict], excludes: str, exclude_protocols: list[str]) -> list[dict]:
    if not excludes and not exclude_protocols:
        return nodes

    new_nodes = []
    for node in nodes:
        if excludes and re.search(excludes, node['tag']):
            continue
        if exclude_protocols and node['type'] in exclude_protocols:
            continue
        new_nodes.append(node)
    return new_nodes


def __rename_nodes(nodes: list[dict], override: dict) -> list[dict]:
    tag_prefix = override.get('tag_prefix')
    tag_suffix = override.get('tag_suffix')

    if not tag_prefix and not tag_suffix:
        return nodes

    for node in nodes:
        if tag_prefix:
            node['tag'] = tag_prefix + node['tag']
        if tag_suffix:
            node['tag'] = node['tag'] + tag_suffix
    return nodes


def __parse_proxies(proxies: list[str]) -> list[dict]:
    """
    node format:
    see: https://sing-box.sagernet.org/configuration/outbound/
    """
    nodelist = []
    for proxy in proxies:
        proxy = proxy.strip()
        if len(proxy) == 0:
            continue
        factory = __get_parser(proxy)
        if not factory:
            continue
        try:
            node = factory(proxy)
        except Exception as e:
            logging.error('parse node failed, %s', e)
        if node:
            nodelist.append(node)
    return nodelist


def __get_parser(proxy: str):
    proto = __get_protocol(proxy)
    return parsers.get_parser(proto)


def __get_protocol(s):
    try:
        m = re.search(r'^(.+?)://', s)
    except Exception as e:
        return None

    if m:
        if m.group(1) == 'hy2':
            s = re.sub(r'^(.+?)://', 'hysteria2://', s)
            m = re.search(r'^(.+?)://', s)
        if m.group(1) == 'wireguard':
            s = re.sub(r'^(.+?)://', 'wg://', s)
            m = re.search(r'^(.+?)://', s)
        if m.group(1) == 'http2':
            s = re.sub(r'^(.+?)://', 'http://', s)
            m = re.search(r'^(.+?)://', s)
        if m.group(1) == 'socks5':
            s = re.sub(r'^(.+?)://', 'socks://', s)
            m = re.search(r'^(.+?)://', s)
        return m.group(1)
