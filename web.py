"""

This is the web component of the technical progress app. To start execute 
start from the bash / terminal: 

pipenv shell
./start
DATABASE_URL="dbname=larry3 user=larry" ./start

"""
import os
import datetime
import io
from flask import Flask, request, session, escape, jsonify, send_file, render_template
from flask_cors import CORS
import psycopg2
import json

from google.oauth2 import id_token
from google.auth.transport import requests

import sql.sql as sql
import utils.dates
import utils.results
import utils.weekly_report as report

print("--- Starting", __file__)
CLIENT_ID = "225894951024-d2b5jugscfmfsp8fr6vd5mqhfl5si3uq.apps.googleusercontent.com"

app = Flask(__name__)
app.secret_key = os.urandom(16)
CORS(app, supports_credentials=True)


@app.route("/")
def hello():
	# session["lfs"] = "Larry"
	# s = escape(str(session))
	# print("Session for this dude:", s)
	return "Hello World! from EvolveU Evaluation."

@app.route("/gsignon", methods = ['POST'])
def google_signon():
	# s = escape(str(session))
	# print("Session for this dude:", s)
	content = request.get_json()
	# print(content)

	try:
		# ask google if they are valid
		idinfo = id_token.verify_oauth2_token(content['user_token'], requests.Request(), CLIENT_ID)
		# print(idinfo)
		# print('--email--', idinfo['email'], idinfo['name'])
		# print('--idtoken--', content['user_token'])

		user = sql.get_user_by_email(idinfo['email'])
		if user:		# registered student
			name = user.name
			admin = user.admin
			new_user = ""
		else:			# not registered so they need to register
			name = idinfo['name']
			admin = False
			new_user = True

		set_email(content, idinfo['email'])

		# print("Session set -- for this dude:", idinfo['email'], content['user_token'])

		return jsonify({
			'new_user': new_user,
			'name': name, 
			'admin': admin}), 200

	except ValueError:
		print('**** Not a valid request ***')

	return jsonify('{}'), 404
# 
# Check to see if the session is still valid
# 
@app.route("/validuser", methods = ['POST'])
def valid_user():

	try:
		content = request.get_json()
		user = get_user(content)
		return jsonify({'name':user.name}), 200
	except KeyError:
		print('**** Not a valid request ***')

	return jsonify('{}'), 404
# 
# Check to see if the session is still valid
# 
@app.route("/signout", methods = ['POST'])
def signout_user():

	try:
		content = request.get_json()
		clear_email(content)
	except KeyError:
		print('**** Not a valid user but we do not care ***')

	return "", 200

# 
# register a new user to the system. The user must have
# already signed on with a valid auth0 provider.
# Today (maybe even when you read this) Google is the
# only auth0 provider implemented.
# 
@app.route("/register", methods = ['POST'])
def register():

	try:
		content = request.get_json()
		email = get_email(content)
		sql.insert_users(content["name"], email, None, False)
		return jsonify({'name':content["name"]}), 200

	except KeyError as e:
		print('**** Not a valid user ***', e)

	return jsonify('{}'), 404

@app.route("/questions")
def questions():
	return jsonify(sql.get_questions())
#
# Get results to display
#
@app.route("/results/", methods = ['POST'])
@app.route("/results/<date>", methods = ['POST'])
def results(date=None):
	# s = escape(str(session))
	# print("results Session for this dude:", s)
	try :
		content = request.get_json()
		user = get_user(content)

		this_monday = utils.dates.my_monday(datetime.datetime.now().date())

		id = user.id
		start_date = user.start_date
		if not start_date:					# New registers do not have a start date
			start_date = this_monday

		# Monday is the day the user wants to see
		if not date:
			monday = this_monday
		else:
			monday = utils.dates.to_date(date)

		next_monday = utils.dates.next_monday(monday)
		last_monday = utils.dates.last_monday(monday)

		if next_monday > this_monday:
			next_monday = ''

		if last_monday < start_date:
			last_monday = ''

		allow_input = True if (this_monday == monday) else False 

		results, going_well, issues, what_to_try  = sql.get_result_object_by_student_date(id, str(monday))

		return jsonify({'results':results,
						'last_monday': str(last_monday), 
						'this_monday': str(monday), 
						'next_monday': str(next_monday),
						'allow_input': allow_input,
						'going_well': going_well,
						'issues': issues,
						'what_to_try': what_to_try})

	except KeyError as e:
		print('**** Not a valid user ***', e)

	return jsonify('{}'), 404
#
# eyJlbWFpbCI6ImxhcnJ5QGV2b2x2ZXUuY2EiLCJpZCI6M30.XFpYCA.MbjGT6HbxkVU5DiTn_a5QLUyLIQ
# eyJlbWFpbCI6ImxhcnJ5QGV2b2x2ZXUuY2EiLCJpZCI6M30.XFpYCA.MbjGT6HbxkVU5DiTn_a5QLUyLIQ
#
@app.route("/update", methods = ['POST'])
def update():
	try :
		content = request.get_json()
		user = get_user(content)

		# print('--Starting update--')

		# print("--update--", user.email,
		# 	content['date'], content['code'], content['value'])

		id = user.id

		row = sql.get_results_by_student_date(id, content['date'])

		if content['type'] == 'score':
			sql.update_result_by_student_date(id, content['date'], content['code'], int(content['value']))
		else:
			sql.update_result_text_student_date(id, content['date'], content['code'], content['value'])
		# print('We should update the text:',content['code'], content['date'], content['code'], int(content['value'])

		return jsonify({'status': 'ok'}), 200

	except KeyError as e:
		print('**** Not a valid user, or data incomplete ***', e)

	return jsonify('{}'), 404
#
#  Add an admin user to the system
#
@app.route("/adduser/<uuid>/")
def adduser(uuid):
	id = request.args.get('id')
	user = request.args.get('user')
	email = request.args.get('email')
	startDate = request.args.get('startDate')

	# sql.insert_users(100,'Larry Shumlich', 'lshumlich@gmail.com', '2018-09-03')

	admin_user = sql.get_user_by_uuid(uuid)
	if admin_user:
		if admin_user.admin:
			sql.insert_users(int(id),user,email,startDate,False)
			return "just playing"

	return '',404
#
# Output Results to a spreadsheet 
# Fix this as a second priority
#
# @app.route("/excel_results/<uuid>/")
# def excel_results(uuid):
# 	user_lookup = sql.get_user_by_uuid(uuid)
# 	if user_lookup:
# 		if user_lookup.admin:
# 			out = io.BytesIO()
# 			wb = utils.results.get_results()
# 			wb.save(out)
# 			out.seek(0)
# 
# 			return send_file(
# 				out, 
# 				mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
# 		        attachment_filename='results.xlsx', 
# 		        as_attachment=True)
# 	return '',404
#
#  ???? Delete Me I Think ???
# Show student progress: Comments / Skill Self Assements / Class Progress
#
@app.route("/comments/<uuid>/")
@app.route("/comments/<uuid>/<date>/")
@app.route("/comments/<uuid>/<date>/<student>/")
def comments(uuid, date=None, student=None):
	#
	# Hard coded today but must be changed
	#
	start_date = '2019-02-11'
	#
	# Makes sure the user is admin
	#
	user_lookup = sql.get_user_by_uuid(uuid)
	if user_lookup:
		if user_lookup.admin:
			report = utils.weekly_report.create_weekly_report(start_date, date, student)
			scroll = utils.dates.scroll_mondays(start_date, date)
			return render_template('comments.html', results=report.results, questions=report.questions, 
								   missing=report.missing, progress=report.class_progress, 
								   date=report.report_date, week=report.week_number,
								   uuid=uuid, scroll=scroll, student=report.student)

	return '',404
# 
# Utilities not to be directly attached to routes for security reasons
# 

valid_email = {}
id_key = "user_token"

def set_email(obj, email):
	valid_email[obj[id_key]] = email

def get_email(obj):
	return valid_email[obj[id_key]]

def clear_email(obj):
	return valid_email.pop(obj[id_key], None)

def clear_sessions():
	valid_email = {}

#
# must be in the session and in the user table
#
def get_user(obj):
	email = valid_email[obj[id_key]]
	user = sql.get_user_by_email(email)
	if not user:
		raise KeyError("user not found in users table")
	return user

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
