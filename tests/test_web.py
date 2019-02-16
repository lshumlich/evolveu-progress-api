# 
# See test_sql for instructions on how to run the tests.
# 
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
# 
# Had to implement session and not use flask directly because
# if two users on the same computer updated their progress
# the cross talked updated the wrong user.
# 
def test_session(client):

	sql.sqlutil.init_session()
	obj = {}		# represents a json object

	with pytest.raises(KeyError):
		web.get_email(obj)

	obj[web.id_key] = "1234"
	web.set_email(obj, "lshumlich@gmail.com")

	assert(web.get_email(obj) == "lshumlich@gmail.com")

	web.clear_email(obj)

	with pytest.raises(KeyError):
		web.get_email(obj)

	web.clear_email(obj) # allow clearing a session that does not exist

	# The same user could be using different browsers
	
	obj[web.id_key] = "1234"
	web.set_email(obj, "lshumlich@gmail.com")

	obj[web.id_key] = "1235"
	web.set_email(obj, "lshumlich@gmail.com")
#
# Test that the user has signed on through auth0 and that it
# is a valid user in the system.
#
def test_get_user(client):

	sql.sqlutil.init_users()

	sql.sqlutil.init_session()
	obj = {}		# represents a json object

	with pytest.raises(KeyError):
		web.get_user(obj)

	#
	# Simulate a session user that is not in the users table to make
	#

	obj = {}		# represents a json object
	email = "lorraine_shumlich@gmail.com"
	obj[web.id_key] = "1234"
	web.set_email(obj, email)

	assert(web.get_email(obj) == "lorraine_shumlich@gmail.com")

	with pytest.raises(KeyError):		# not in the database
		web.get_user(obj)

#
# Test if the session is still valid and signout
#
def test_validuser_signout(client):

	sql.sqlutil.init_session()

	rv = client.post('/validuser',json={
    }, follow_redirects=True)
	assert(rv.status_code == 404)

	# signout should just work
	rv = client.post('/signout',json={
		web.id_key : 'asdf',
    }, follow_redirects=True)
	assert(rv.status_code == 200)

	obj = simulate_invalid_user()
	rv = client.post('/validuser',json={
		web.id_key : obj[web.id_key],
    }, follow_redirects=True)
	assert(rv.status_code == 404)

	# signout should just work
	rv = client.post('/signout',json={
		web.id_key : obj[web.id_key],
    }, follow_redirects=True)
	assert(rv.status_code == 200)

	obj = simulate_valid_user()
	rv = client.post('/validuser',json={
		web.id_key : obj[web.id_key],
	}, follow_redirects=True)
	data = json.loads(rv.data)
	assert(rv.status_code == 200)
	assert(data["name"] == "Larry Shumlich")

	# signout should just work
	rv = client.post('/signout',json={
		web.id_key : obj[web.id_key],
    }, follow_redirects=True)
	assert(rv.status_code == 200)

	# once signout the user should not be valid anymore
	rv = client.post('/validuser',json={
		web.id_key : obj[web.id_key],
	}, follow_redirects=True)
	data = json.loads(rv.data)
	assert(rv.status_code == 404)

	# print("Data:", data)
#
# Test if the session is still valid 
#
def test_signout(client):

	sql.sqlutil.init_session()
	rv = client.post('/signout',json={
    }, follow_redirects=True)
	assert(rv.status_code == 200)

	obj = simulate_invalid_user()
	rv = client.post('/signout',json={
		web.id_key : obj[web.id_key],
    }, follow_redirects=True)
	assert(rv.status_code == 200)

	obj = simulate_valid_user()
	rv = client.post('/signout',json={
		web.id_key : obj[web.id_key],
	}, follow_redirects=True)
	data = json.loads(rv.data)
	assert(rv.status_code == 200)
	# assert(data["name"] == "Larry Shumlich")
	# print("Data:", data)

# 
# Self register a new user to the system
# 
def test_register(client):

	sql.sqlutil.init_session()
	sql.sqlutil.init_users()

	#
	# Must have a valid auth0 login before you can
	# self register
	#

	rv = client.post('/register',json={
	    }, follow_redirects=True)
	assert(rv.status_code == 404)

	#
	# Simulate a registered user
	#

	obj = {}		# represents a json object
	email = "lorraine_shumlich@gmail.com"
	obj[web.id_key] = "1234"
	web.set_email(obj, email)

	#
	# Make sure the register route adds the new user correctly 
	#
	# print("----- Somethings fishy ----")

	rv = client.post('/register',json={
			web.id_key : obj[web.id_key],
			"name": "Lorraine Shumlich2"
	    }, follow_redirects=True)
	assert(rv.status_code == 200)

	user = sql.sql.get_user_by_email(email)
	assert(user.admin == False)

def test_questions(client):
	rv = client.get('/questions')
	assert(rv.status_code == 200)


def test_results(client):

	sql.sqlutil.init_session()
	rv = client.post('/results/',json={
    }, follow_redirects=True)
	assert(rv.status_code == 404)

	obj = simulate_invalid_user()
	rv = client.post('/results/',json={
		web.id_key : obj[web.id_key],
    }, follow_redirects=True)
	assert(rv.status_code == 404)

	obj = simulate_valid_user()
	rv = client.post('/results/',json={
		web.id_key : obj[web.id_key],
    }, follow_redirects=True)
	assert(rv.status_code == 200)

def test_updates(client):

	sql.sqlutil.init_session()
	rv = client.post('/update', json={
	    }, follow_redirects=True)
	assert(rv.status_code == 404)

	obj = simulate_invalid_user()
	rv = client.post('/update',json={
		web.id_key : obj[web.id_key],
    }, follow_redirects=True)
	assert(rv.status_code == 404)

	print("--- Should be a good user ---")
	obj = simulate_valid_user()
	users = sql.sql.get_users()
	# user = users[0]

	rv = client.post('/update', json={
			web.id_key : obj[web.id_key],
	        'date': '2018-09-03',
	        'type': 'score',
	        'code': 'sql',
	        'value': '7'
	    }, follow_redirects=True)
	assert(rv.status_code == 200)


# 
# I think we can delete this one.
# 
# def test_add_user(client):
# 	rv = client.get('/adduser/uuidbad/')
# 	assert(rv.status_code == 404)

# 	# need an admin user
# 	user = sql.sql.get_user_by_email('lshumlich@gmail.com')
# 	uuid = user.uuid
# 	args = '?id=1002&user=Jes%20Shumlich&email=jes_shumlich@gmail.com&startDate=2018-09-10'

# 	rv = client.get('/adduser/' + uuid + '/' + args)
# 	assert(rv.status_code == 200)

# -------------------------------------
#
# Fix this one later
#

# def test_excel_results(client):
# 	rv = client.get('/excel_results/uuidbad/')
# 	assert(rv.status_code == 404)

# 	# need an admin user
# 	user = sql.sql.get_user_by_email('lshumlich@gmail.com')
# 	uuid = user.uuid

# 	rv = client.get('/excel_results/' + uuid + '/')
# 	assert(rv.status_code == 200)

def test_comments(client):
	rv = client.get('/comments/uuidbad/')
	assert(rv.status_code == 404)

	# need an admin user
	user = sql.sql.get_user_by_email('lshumlich@gmail.com')
	uuid = user.uuid

	rv = client.get('/comments/' + uuid + '/')
	assert(rv.status_code == 200)

# 	# data = json.loads(rv.data)
# 	# print('----rv---',rv)
# 	# print('----rv.data---', rv.data)
# 	# print('----data---', data)


def simulate_valid_user():
	sql.sql.delete_all_sessions()
	obj = {}		# represents a json object
	obj[web.id_key] = "1234"
	web.set_email(obj, "lshumlich@gmail.com") # User is in the database
	return obj

def simulate_invalid_user():
	sql.sql.delete_all_sessions()
	obj = {}		# represents a json object
	obj[web.id_key] = "1234"
	web.set_email(obj, "larry_shumlich@gmail.com") # User is not in the database
	return obj
