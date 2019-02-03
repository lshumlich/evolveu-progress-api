
import pytest

from flask import json

# from google.oauth2 import id_token
# from google.auth.transport import requests

import sql.sql
import sql.sqlutil

import web

@pytest.fixture
def client():

    web.app.config['TESTING'] = True
    client = web.app.test_client()

    yield client


def test_root(client):
	rv = client.get('/')
	# print('----rv---',rv)
	# print('----rv.headers---',rv.headers)
	# print('----rv.status---',rv.status)
	# print('----rv.status_code---',rv.status_code)
	# print('----rv.data---',rv.data)
	assert(b'EvolveU Evaluation' in rv.data)


def test_register(client):
	rv = client.get('/register/uuiddummy')
	assert(rv.status_code == 404)

	sql.sqlutil.init_users()
	users = sql.sql.get_users()

	user = users[0]
	uuid = user.uuid
	rv = client.get('/register/' + uuid)
	assert(rv.status_code == 200)

	data = json.loads(rv.data)
	assert(data['id'] == user.id)
	assert(data['name'] == user.name)


def test_questions(client):
	rv = client.get('/questions')
	assert(rv.status_code == 200)


def test_results(client):
	rv = client.get('/results/uuidbad/')
	assert(rv.status_code == 404)

	users = sql.sql.get_users()
	user = users[0]
	uuid = user.uuid

	rv = client.get('/results/' + uuid + '/')
	assert(rv.status_code == 200)

	data = json.loads(rv.data)


def test_updates(client):
	rv = client.post('/update', json={
	        'uuid':'uuidthatsbad'
	    }, follow_redirects=True)
	assert(rv.status_code == 404)

	users = sql.sql.get_users()
	user = users[0]
	uuid = user.uuid

	rv = client.post('/update', json={
	        'uuid': uuid,
	        'date': '2018-09-03',
	        'type': 'score',
	        'code': 'sql',
	        'value': '7'
	    }, follow_redirects=True)
	assert(rv.status_code == 200)


def test_add_user(client):
	rv = client.get('/adduser/uuidbad/')
	assert(rv.status_code == 404)

	# need an admin user
	user = sql.sql.get_user_by_email('lshumlich@gmail.com')
	uuid = user.uuid
	args = '?id=1002&user=Jes%20Shumlich&email=jes_shumlich@gmail.com&startDate=2018-09-10'

	rv = client.get('/adduser/' + uuid + '/' + args)
	assert(rv.status_code == 200)


def test_excel_results(client):
	rv = client.get('/excel_results/uuidbad/')
	assert(rv.status_code == 404)

	# need an admin user
	user = sql.sql.get_user_by_email('lshumlich@gmail.com')
	uuid = user.uuid

	rv = client.get('/excel_results/' + uuid + '/')
	assert(rv.status_code == 200)


def test_comments(client):
	rv = client.get('/comments/uuidbad/')
	assert(rv.status_code == 404)

	# need an admin user
	user = sql.sql.get_user_by_email('lshumlich@gmail.com')
	uuid = user.uuid

	rv = client.get('/comments/' + uuid + '/')
	assert(rv.status_code == 200)

	# data = json.loads(rv.data)
	# print('----rv---',rv)
	# print('----rv.data---', rv.data)
	# print('----data---', data)

