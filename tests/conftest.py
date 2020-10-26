import os
import tempfile


import pytest

from flaskr import create_app
from flaskr.db import haskell_collection, prolog_collection

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
