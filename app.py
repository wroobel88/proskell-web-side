from flask import Flask, jsonify, request, json, Response
from pymongo import MongoClient
from pprint import pprint
import time
from bson.json_util import loads, dumps
from bson import ObjectId

app = Flask(__name__)
app.config['DEBUG'] = True


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient("mongodb+srv://root:asd@cluster0.yan5i.mongodb.net/sample_restaurants?retryWrites=true&w=majority")
db = client.students
haskell_collection = db.haskell
prolog_collection = db.prolog


def get_one_attempt(language):
    if language == 'haskell':
        a = JSONEncoder().encode(haskell_collection.find_one())
    else:
        a = JSONEncoder().encode(prolog_collection.find_one())

    return a


def get_all_attempts(language):
    attempts = []
    if language == 'haskell':
        results = haskell_collection.find()
    else:
        results = prolog_collection.find()
    for a in results:
        b = JSONEncoder().encode(a)
        attempts.append(b)
    return attempts


def add_attempt(data, language):
    user_request = {
        'language': language,
        'userid': data['userid'],
        'code': data['code'],
        'timestamp': time.time()
    }
    if language == 'haskell':
        res = haskell_collection.insert_one(user_request).inserted_id
        added = JSONEncoder().encode(haskell_collection.find_one(res))
        return added
    else:
        return prolog_collection.insert_one(user_request)


@app.route('/haskell', methods=['GET', 'POST'])
def get_attemps():
    if request.method == 'GET':
        a = get_one_attempt('haskell')
        return Response(a, mimetype='application/json')
    if request.method == 'POST':
        result = add_attempt(loads(request.data), 'haskell')
        return Response(result, mimetype='application/json')


@app.route('/haskell/all')
def get_all_attemps():
    all_items = get_all_attempts('haskell')
    return Response(all_items, mimetype='application/json')
