import os
import tempfile

import pytest

from filmlog import app as application


@pytest.fixture
def client():
#    db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
#    flaskr.app.config['TESTING'] = True
    client = app.test_client()

#    with flaskr.app.app_context():
#        flaskr.init_db()

    yield client

    os.close(db_fd)
#    os.unlink(flaskr.app.config['DATABASE'])
