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

haskell_tests_collection = mongo.db.haskell_tests


bp = Blueprint('user_attempts', __name__)

CORS(bp)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def get_last_attempt(language, userid, exercise_number):
    collection = haskell_collection if language == 'haskell' else prolog_collection
    results = collection.find({'language': language, 'exerciseNo': exercise_number, 'userid': userid})
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

def normalize_white_characters(value):
    return value.replace('\\n', '\n').replace('\\t', '\t')

def compare_results(a, b):
    if len(a) == len(b):
        for x, y in zip(a, b):
            if x == y:
                continue
            else:
                return f'{x} does not equal {y}'
    elif len(a) < len(b):
        return f'Expected output is shorter than your answer'
    else:
        return f'Expected output is longer than your answer'




def add_attempt(data, language):
    user_request = {
        'language': language,
        'userid': data['userid'],
        'code': data['code'],
        'exerciseNo': data['exerciseNo'],
    }
    # save attempt to db
    collection = haskell_collection if language == 'haskell' else prolog_collection
    res = collection.insert_one(user_request).inserted_id
    added = JSONEncoder().encode(haskell_collection.find_one(res))
    
    
    # fetch exercise tests
    tests_collection = haskell_tests_collection if language == 'haskell' else haskell_tests_collection
    test = tests_collection.find_one({"exerciseNo": int(data['exerciseNo'])})

    # merge user_request and tests    
    user_request.update({'tests': test['tests'], 'timeoutMs': 1000, 'timestamp': time.time()})

    # send code to check
    request_data = parse_json(user_request)

    # r = requests.post('http://proskell-runtime:4000/', json=request_data)
    check_result_ = requests.post('http://localhost:4000/', json=request_data)
    # check results
    check_result = loads(check_result_.content)
    response = { 'data': [], 'error': None}
    if check_result['result_status'] == 1:
        response['error'] = 'compilation error'
        return response

    numer_of_tests = len(check_result['tests'])
    for i, test in enumerate(check_result['tests']):
        if check_result['result_status'] == 1:
            response['error'] = 'some error'
            break
        else: 
            if check_result['result_status'] == 0:
                expected_result = normalize_white_characters(test['result'])
                test_result = test['result_stdout'].rstrip('\n')
                if expected_result == test_result:
                    response['data'].append(f'Test number {i} passed.')
                else:
                    comparision = compare_results(expected_result, test_result)
                    if len(comparision) == 0:
                        response['data'].append(f'Test number {i} passed.')
                    else:
                        response['data'].append(f'Test number {i} is faulty: {comparision}')
            
    return response


@ bp.route('/<language>', methods=['POST'])
@ cross_origin()
def add_attemps(language):
    if request.method == 'POST':
        added_attempt = add_attempt(loads(request.data), language)
        response = JSONEncoder().encode(added_attempt)
        return Response(response, mimetype='application/json')

@ bp.route('/<language>/<userid>/<exercise_number>', methods=['GET'])
@ cross_origin()
def get_attempts(language, userid, exercise_number):
    if request.method == 'GET':
        a = get_last_attempt(language, userid, exercise_number)
        return Response(a, mimetype='application/json')

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
