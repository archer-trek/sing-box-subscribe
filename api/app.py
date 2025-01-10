import json
from flask import Flask, make_response

from subscribe import config

app = Flask(__name__)


@app.route('/config/<path:token>', methods=['GET'])
def get_config(token):
    conf = config.gen_config(token)
    if not conf:
        return '', 404

    response = make_response(json.dumps(conf, indent=2, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = 200
    return response


def run():
    app.run(host='0.0.0.0', port=8080)
