import os

from flask import Flask


def create_app(test_config=None, mongo_conf='flaskr.settings'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # app.config.from_object(mongo_conf)
    app.config["MONGO_URI"] = 'mongodb+srv://asd:asd@cluster0.yan5i.mongodb.net/students?retryWrites=true&w=majority'
    from .database import mongo

    MONGO_URI = ''
    mongo.init_app(app)

    from .user_attempts import bp
    app.register_blueprint(bp)
    # app.add_url_rule('/', endpoint='index')

    from .tests import tests
    app.register_blueprint(tests, url_prefix='/tests')
    # app.add_url_rule(url_prefix ='/test', endpoint='index')

    return app
