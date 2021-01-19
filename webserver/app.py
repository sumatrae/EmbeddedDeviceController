import os
import flask
from flask import Flask
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


@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":
        return flask.render_template("index.html")

    elif flask.request.method == "POST":
        return flask.render_template("index.html")

    flask.render_template('index.html')


@app.route("/index1", methods=["GET", "POST"])
def index1():
    if flask.request.method == "GET":
        return flask.render_template("index1.html", ui_config = ui_config)

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


app.run(host="0.0.0.0", port=9018)
