from socket import timeout
from flask import (
    Blueprint, request, Response, json, jsonify
)
import requests
import time
from bson.json_util import loads, dumps
from bson import ObjectId
from .database import mongo
from flask_cors import CORS, cross_origin


haskell_collection = mongo.db.haskell
prolog_collection = mongo.db.prolog

bp = Blueprint('user_attempts', __name__)

CORS(bp)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def get_one_attempt(language):
    collection = haskell_collection if language == 'haskell' else prolog_collection
    a = JSONEncoder().encode(collection.find_one())

    return a


def get_all_attempts(language):
    attempts = []
    collection = haskell_collection if language == 'haskell' else prolog_collection
    results = collection.find()

    for a in results:
        attempts.append(a)

    return JSONEncoder().encode({'data': attempts, 'error': None})

def parse_json(data):
    return json.loads(dumps(data))


def add_attempt(data, language):
    user_request = {
        'language': language,
        'userid': data['userid'],
        'code': data['code'],
        'timestamp': time.time(),
        'timeoutMs': 1000,
        'tests': [
            {"input": "input1"},
            {"input": "input2"},
            {"input": "input3"},
            {"input": "input4"},
            {"input": "input5"}
        ]
    }
    # save attempt to db
    collection = haskell_collection if language == 'haskell' else prolog_collection
    res = collection.insert_one(user_request).inserted_id
    added = JSONEncoder().encode(haskell_collection.find_one(res))
    # send code to check
    request_data = parse_json(user_request)

    r = requests.post('http://proskell-runtime:4000/', json=request_data)

    return r


@ bp.route('/<language>', methods=['GET', 'POST'])
@ cross_origin()
def get_add_attemps(language):
    if request.method == 'GET':
        a = get_one_attempt(language)
        return Response(a, mimetype='application/json')
    if request.method == 'POST':
        response = add_attempt(loads(request.data), language)

        # Enable Access-Control-Allow-Origin
        # response.headers.add("Access-Control-Allow-Origin", "*")
        return Response(response, mimetype='application/json')


@ bp.route('/<language>/all')
@ cross_origin()
def get_all_attemps(language):
    all_items = get_all_attempts(language)
    return Response(all_items, mimetype='application/json')


@ bp.route('/<language>/<key>', methods=['DELETE'])
@ cross_origin()
def delete_by_key(language, key):
    if request.method == 'DELETE':
        if language == 'haskell':
            haskell_collection.delete_one({"_id": ObjectId(key)})
        elif language == 'prolog':
            prolog_collection.delete_one({"_id": ObjectId(key)})
        return f'Document {key} removed.'
