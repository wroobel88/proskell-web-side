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

haskell_tests_collection = mongo.db.haskell_tests
tests = Blueprint('tests', __name__, url_prefix ='/tests')

CORS(tests)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def parse_json(data):
    return json.loads(dumps(data))


def get_one_test(language, exercise_number):
    collection = haskell_tests_collection if language == 'haskell' else haskell_tests_collection
    test = collection.find_one({"exerciseNo": int(exercise_number)} )
    a = JSONEncoder().encode(test)
    return a


def add_test(data):
    test = {
        'language': data['language'],
        'exerciseNo': data['exerciseNo'],
        'tests': data['tests'],
    }
    language = data['language']
    # save test to db
    collection = haskell_tests_collection if language == 'haskell' else haskell_tests_collection
    res = collection.insert_one(test).inserted_id
    added = JSONEncoder().encode(haskell_tests_collection.find_one(res))
    return added

@ tests.route('/<language>/<exercise_number>', methods=['GET', 'POST'])
@ cross_origin()
def get_test(language, exercise_number):
    if request.method == 'GET':
        test = get_one_test(language, exercise_number)
        return Response(test, mimetype='application/json')
 


@ tests.route('', methods=['POST'])
@ cross_origin()
def add_tests():
    if request.method == 'POST':
        data = loads(request.data)
        response = add_test(data)
        return Response(response, mimetype='application/json')
