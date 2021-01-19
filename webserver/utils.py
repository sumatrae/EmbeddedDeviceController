import os
import json
from collections import defaultdict
from functools import wraps

import flask


ALLOWED_EXTENSIONS = ['json', ]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def send_error(msg):
    return flask.jsonify(
        {
            'message': msg,
            'status': 'fail'
        }
    )


def send_info(msg):
    return flask.jsonify(
        {
            'message': msg,
            'status': 'success'
        }
    )



def dict_msg(msgs):
    return '; '.join(['[{}] {}'.format(v, k) for (k, v) in msgs.items()])


def load_config(filename, ordered = False):
    with open(filename,encoding="utf-8") as fd:
        if ordered == False:
            config = json.load(fd)
        else:
            from collections import OrderedDict
            config = json.load(fd, object_pairs_hook= OrderedDict)
    return config
