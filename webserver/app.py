"""
Flask service
"""
import os
import flask
from flask import Flask, session
import config
import utils
from utils import load_config, save_config
from werkzeug.utils import secure_filename

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
    tempfile = f"{ip}.json"
    if not os.path.exists(tempfile):
        import shutil
        shutil.copy("nsm.json", tempfile)

    nsm_config = load_config(tempfile)

    if flask.request.method == "GET":
        return flask.render_template(
            "index1.html", ui_config=ui_config, nsm_config=nsm_config)

    elif flask.request.method == "POST":
        return flask.render_template("index1.html")

    flask.render_template('index1.html')


@app.route("/apply", methods=["GET", ])
def apply():
    ip = get_user_ip(flask.request)
    session["ip"] = ip
    tempfile = f"{ip}.json"
    if os.path.exists(tempfile):
        import shutil
        shutil.copy(tempfile, "nsm.json")

    nsm_config = load_config(tempfile)
    return flask.render_template(
        "index1.html", ui_config=ui_config, nsm_config=nsm_config)


@app.route("/getconfig", methods=["GET", ])
def getuiconfig():
    ip = get_user_ip(flask.request)
    session["ip"] = ip
    tempfile = f"{ip}.json"
    if not os.path.exists(tempfile):
        import shutil
        shutil.copy("nsm.json", tempfile)

    nsm_config = load_config(tempfile)
    return flask.jsonify(nsm_config)


@app.route("/nsm/<config_id>", methods=["GET", "POST"])
def getnsmconfig(config_id):
    if flask.request.method == "GET":
        nsm_config = load_config("nsm.json")
        return flask.jsonify(nsm_config)

    elif flask.request.method == "POST":
        ip = get_user_ip(flask.request)
        nsm_config = load_config(f"{ip}.json")
        print(config_id)

        form = flask.request.form
        if config_id in nsm_config.keys():
            for key in nsm_config[config_id].keys():
                value = form.get(f"{config_id}_{key}", '')
                if value != '':
                    nsm_config[config_id][key] = value

            save_config(f"{ip}.json", nsm_config)

            return flask.render_template(
                "index1.html", ui_config=ui_config, nsm_config=nsm_config)


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


@app.route('/download', methods=['GET'])
def download():
    try:
        abs_file_path = "nsm.json"
        if not os.path.exists(abs_file_path):
            return flask.jsonify(
                {
                    'message': "Not found download file",
                    'status': 'success',
                }
            )

        def generate():
            chunk_size = 10 * 1024 * 1024

            with open(abs_file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        response = flask.Response(
            generate(), mimetype='application/octet-stream')

        output_filename = "nsm.json"
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format(
            output_filename)
        response.headers['content-length'] = os.stat(
            str(abs_file_path)).st_size
    except Exception as e:
        return flask.jsonify(
            {
                'message': "Download exception:{}".format(e),
                'status': 'success',
            }
        )

    return response


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a json file and import it's content to database.
    """
    if 'file' not in flask.request.files:
        return utils.send_error('No file provided to upload!')
    _file = flask.request.files['file']
    if _file.filename == '':
        return utils.send_error('No selected file!')
    if not _file or not utils.allowed_file(_file.filename):
        return utils.send_error('Invalid file type!')

    filename = secure_filename(_file.filename)
    ip = get_user_ip(flask.request)
    session["ip"] = ip
    tempfile = f"{ip}.json"
    if os.path.exists(tempfile):
        os.remove(tempfile)

    _file.save(filename)
    os.rename(filename, tempfile)

    nsm_config = load_config(tempfile)

    return flask.render_template(
        "index1.html", ui_config=ui_config, nsm_config=nsm_config)
    # return flask.jsonify(
    #     {
    #         'message': "Upload complete; " + utils.dict_msg(nsm_config),
    #         'status': 'success',
    #     }
    # )


app.run(host="0.0.0.0", port=9018)
