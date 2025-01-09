from flask import Flask

from subscribe import config

app = Flask(__name__)


@app.route('/config/<path:token>', methods=['GET'])
def get_config(token):
    conf = config.gen_config(token)
    if not conf:
        return '', 404
    return conf


def run():
    app.run(host='0.0.0.0', port=8080)
