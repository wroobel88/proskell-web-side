from flask import Flask
from pymongo import MongoClient
from pprint import pprint
from time import time
app = Flask(__name__)
app.config['DEBUG'] = True

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient("mongodb+srv://root:asd@cluster0.yan5i.mongodb.net/sample_restaurants?retryWrites=true&w=majority")
db = client.students
collection = db.haskell

request = {
    'language': 'haskell',
    'userid': 114986,
    'code': "main = do putStrLn \"Haskell main()\"\n          line <- getLine\n          putStrLn (\"First line from stdin:\" ++ line)",
    'timestamp': time()
}
added_record = collection.find_one()

@app.route('/')
@app.route('/hello')
def hello_world():
    return 'Hello, Dickhead!'