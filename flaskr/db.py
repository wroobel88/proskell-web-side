from pymongo import MongoClient

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient("mongodb+srv://root:asd@cluster0.yan5i.mongodb.net/sample_restaurants?retryWrites=true&w=majority")
db = client.students
haskell_collection = db.haskell
prolog_collection = db.prolog

