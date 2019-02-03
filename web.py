"""

This is the web component of the technical progress app. To start execute 
start from the bash / terminal: 

pipenv shell
./start
DATABASE_URL="dbname=larry3 user=larry" ./start

"""
import datetime
import io
from flask import Flask, send_file
from flask import jsonify
from flask import request
from flask import render_template
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
CORS(app)

@app.route("/")
def hello():
	return "Hello World! from EvolveU Evaluation"


@app.route("/gsignon", methods = ['POST'])
def google_signon():
	content = request.get_json()
	# print(content)

	try:
		idinfo = id_token.verify_oauth2_token(content['idtoken'], requests.Request(), CLIENT_ID)
		print(idinfo)
		print('--email--', idinfo['email'])
		user = sql.get_user_by_email(idinfo['email'])
		if user:
			return jsonify({'id':user.id,'name':user.name,'uuid':user.uuid}), 200

	except ValueError:
		print('**** Not a valid request ***')

	return jsonify('{}'), 404


@app.route("/register/<uuid>")
def register(uuid=None):
	user = sql.get_user_by_uuid(uuid)
	if user:
		return jsonify({'id':user.id,'name':user.name}), 200
	return jsonify('{}'), 404

@app.route("/questions")
def questions():
	return jsonify(sql.get_questions())
#
# Get results to display
#
@app.route("/results/<uuid>/")
@app.route("/results/<uuid>/<date>")
def results(uuid=None, date=None):

	user = sql.get_user_by_uuid(uuid)
	if not user:
		return '',404

	id = user.id
	start_date = user.start_date

	this_monday = utils.dates.my_monday(datetime.datetime.now().date())

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

	# print(this_monday, monday)
	allow_input = True if (this_monday == monday) else False 
	# allow_input = False

	results, going_well, issues, what_to_try  = sql.get_result_object_by_student_date(id, str(monday))

	return jsonify({'results':results, 
					'last_monday': str(last_monday), 
					'this_monday': str(monday), 
					'next_monday': str(next_monday),
					'allow_input': allow_input,
					'going_well': going_well,
					'issues': issues,
					'what_to_try': what_to_try})
#
# 
#
@app.route("/update", methods = ['POST'])
def update():
	content = request.get_json()
	# print('--- content ---', content)

	user = sql.get_user_by_uuid(content['uuid'])
	if not user:
		return '',404
	id = user.id

	row = sql.get_results_by_student_date(id, content['date'])


	if content['type'] == 'score':
		sql.update_result_by_student_date(id, content['date'], content['code'], int(content['value']))
	else:
		sql.update_result_text_student_date(id, content['date'], content['code'], content['value'])
		# print('We should update the text:',content['code'], content['date'], content['code'], int(content['value'])

	return jsonify({'status': 'ok'}), 200
#
#  Add a user to the system
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
#
@app.route("/excel_results/<uuid>/")
def excel_results(uuid):
	user_lookup = sql.get_user_by_uuid(uuid)
	if user_lookup:
		if user_lookup.admin:
			out = io.BytesIO()
			wb = utils.results.get_results()
			wb.save(out)
			out.seek(0)

			return send_file(
				out, 
				mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		        attachment_filename='results.xlsx', 
		        as_attachment=True)
	return '',404
#
# Show student progress: Comments / Skill Self Assements / Class Progress
#
@app.route("/comments/<uuid>/")
@app.route("/comments/<uuid>/<date>/")
@app.route("/comments/<uuid>/<date>/<student>/")
def comments(uuid, date=None, student=None):
	#
	# Hard coded today but must be changed
	#
	start_date = '2018-09-10'
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

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
