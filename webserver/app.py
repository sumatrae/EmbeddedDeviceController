import os
import flask
from flask import Flask, session
import config
from utils import load_config

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_object(config.Config)
app.config["DEBUG"] = True
ui_config = load_config("ui.json", ordered=True)


@app.route("/ping", methods=["GET"])
def ping():
    if flask.request.method == "GET":
        return flask.jsonify({"ping": "tong"})


@app.route("/test", methods=["GET", "POST"])
def test():
    if flask.request.method == "GET":
        return flask.render_template("index.html")

    elif flask.request.method == "POST":
        return flask.render_template("index.html")

    flask.render_template('index.html')


def get_user_ip(request):
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For']
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


@app.route("/", methods=["GET", "POST"])
def index():
    ip = get_user_ip(flask.request)
    session["ip"] = ip
    tempfile = f"{ip}.txt"
    if not os.path.exists(tempfile):
        import shutil
        shutil.copy("nsm.json", tempfile)

    nsm_config = load_config(tempfile)

    if flask.request.method == "GET":
        return flask.render_template("index1.html", ui_config=ui_config, nsm_config=nsm_config)

    elif flask.request.method == "POST":
        return flask.render_template("index1.html")

    flask.render_template('index1.html')


@app.route("/ui", methods=["GET", ])
def getuiconfig():
    return flask.jsonify(ui_config)


@app.route("/nsm", methods=["GET", "POST"])
def getnsmconfig():
    nsm_config = load_config("nsm.json")
    return flask.jsonify(nsm_config)


def set_network(config):
    pass


def set_db37(config):
    pass


def set_db25(config):
    pass


def set_trig_r(config):
    pass


def set_pos_trig_in(config):
    pass


@app.route("/set/<config>", methods=["GET", "POST"])
def setconfig(config=None):
    response = {"status": "NOK",
                "request": f"/set/{config}",
                "response": ""}

    if config is None:
        response["response"] = "config is None"

    if flask.request.method == "GET":
        # data = flask.request.json
        data = {
            "network": {
                "ip": "192.168.10.1",
                "netmask": "255.255.255.0",
                "gateway": "192.168.10.1",
                "dns": "144.144.144.144"
            },
            "db37beamsteer": {
                "address": "",
                "enable": "false",
                "output": "",
                "trigger_edge": "",
                "trigger_enable": "false",
                "msb_level": "",
                "data_level": ""
            },
            "db25_1": {
                "address": "",
                "enable": "false",
                "output": "",
                "msb_level": "",
                "data_level": ""
            },
            "db25_2": {
                "address": "",
                "enable": "false",
                "output": "",
                "msb_level": "",
                "data_level": ""
            },
            "db25_3": {
                "address": "",
                "enable": "false",
                "output": "",
                "msb_level": "",
                "data_level": ""
            },
            "recr": {
                "trigger_enable": "false",
                "trigger_level": "",
                "pluse_width": "",
                "r_enable": "",
                "r_trig_edge": ""
            },
            "lo": {
                "trigger_enable": "false",
                "trigger_level": "",
                "pluse_width": "",
                "r_enable": "",
                "r_trig_edge": ""
            },
            "src": {
                "trigger_enable": "false",
                "trigger_level": "",
                "pluse_width": "",
                "r_enable": "",
                "r_trig_edge": ""
            },
            "pos_trig_in": {
                "r_enable": "",
                "r_trig_edge": ""
            }
        }
        for config in data.items():
            print(config)

    response["response"] = "config finish"
    return flask.jsonify(response)


app.run(host="0.0.0.0", port=9018)
