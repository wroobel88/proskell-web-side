from flask import (
    Blueprint, request, Response, json
)
import requests
import time
from bson.json_util import loads
from bson import ObjectId
from .database import mongo

haskell_collection = mongo.db.haskell
prolog_collection = mongo.db.prolog

bp = Blueprint('user_attempts', __name__)


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


def add_attempt(data, language):
    user_request = {
        'language': language,
        'userid': data['userid'],
        'code': data['code'],
        'timestamp': time.time()
    }
    # save attempt to db
    collection = haskell_collection if language == 'haskell' else prolog_collection
    res = collection.insert_one(user_request).inserted_id
    added = JSONEncoder().encode(haskell_collection.find_one(res))
    # send code to check
    r = requests.get('http://localhost:4000/')

    return added


@bp.route('/<language>', methods=['GET', 'POST'])
def get_add_attemps(language):
    if request.method == 'GET':
        a = get_one_attempt(language)
        return Response(a, mimetype='application/json')
    if request.method == 'POST':
        result = add_attempt(loads(request.data), language)
        return Response(result, mimetype='application/json')


@bp.route('/<language>/all')
def get_all_attemps(language):
    all_items = get_all_attempts(language)
    return Response(all_items, mimetype='application/json')


@bp.route('/<language>/<key>', methods=['DELETE'])
def delete_by_key(language, key):
    if request.method == 'DELETE':
        if language == 'haskell':
            haskell_collection.delete_one({"_id": ObjectId(key)})
        elif language == 'prolog':
            prolog_collection.delete_one({"_id": ObjectId(key)})
        return f'Document {key} removed.'
