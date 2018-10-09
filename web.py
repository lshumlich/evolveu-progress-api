"""

This is the web component of the technical progress app. To start execute 
start from the bash / terminal: 

./start
DATABASE_URL="dbname=larry2 user=larry" ./start

"""
import datetime
import io
from flask import Flask, send_file
from flask import jsonify
from flask import request
from flask import render_template
from flask_cors import CORS
# from openpxl import Workbook
import psycopg2
import json
import sql.sql as sql
import utils.dates
import utils.results

print("--- Starting", __file__)

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
	return "Hello World! from EvolveU Evaluation"

@app.route("/register/<uuid>")
def register(uuid=None):
	user = sql.get_user_by_uuid(uuid)
	if user:
		return jsonify({'id':user[0][0],'name':user[0][1]}), 200
	return jsonify('{}'), 404

@app.route("/questions")
def questions():
	return jsonify(sql.get_questions())

@app.route("/results/<uuid>/")
@app.route("/results/<uuid>/<date>")
def results(uuid=None, date=None):

	user = sql.get_user_by_uuid(uuid)
	if not user:
		return '',404

	# print(user)
	id = user[0][0]
	start_date = user[0][2]
	# print (start_date)

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

@app.route("/update", methods = ['POST'])
def update():
	content = request.get_json()
	# print(content)

	user = sql.get_user_by_uuid(content['uuid'])
	if not user:
		return '',404
	id = user[0][0]

	row = sql.get_results_by_student_date(id, content['date'])


	if content['type'] == 'score':
		sql.update_result_by_student_date(id, content['date'], content['code'], int(content['value']))
	else:
		sql.update_result_text_student_date(id, content['date'], content['code'], content['value'])
		# print('We should update the text:',content['code'], content['date'], content['code'], int(content['value'])

	return jsonify({'status': 'ok'}), 200


#
# 
#
@app.route("/adduser/<uuid>/")
def adduser(uuid):
	# print(request)
	# print(request.args)
	print('"'+uuid+'"')
	id = request.args.get('id')
	user = request.args.get('user')
	email = request.args.get('email')
	startDate = request.args.get('startDate')

	# sql.insert_users(100,'Larry Shumlich', 'lshumlich@gmail.com', '2018-09-03')

	user_lookup = sql.get_user_by_uuid(uuid)
	print(user_lookup)
	if user_lookup:
		print('Admin:', user_lookup[0][3])
		admin = user_lookup[0][3]
		if admin:
			print('inserting')
			sql.insert_users(int(id),user,email,startDate,False)

			return "just playing"

	print('returning a 404')
	return '',404

@app.route("/excel_results/<uuid>/")
def excel_results(uuid):
	user_lookup = sql.get_user_by_uuid(uuid)
	print(user_lookup)
	if user_lookup:
		print('Admin:', user_lookup[0][3])
		admin = user_lookup[0][3]
		if admin:
			out = io.BytesIO()
			wb = utils.results.get_results()
			wb.save(out)
			out.seek(0)

			return send_file(
				out, 
				mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		        attachment_filename='results.xlsx', 
		        as_attachment=True)
	print('returning a 404')
	return '',404

@app.route("/comments/<uuid>/<date>/")
def comments(uuid, date):
	user_lookup = sql.get_user_by_uuid(uuid)
	print(user_lookup)
	if user_lookup:
		print('Admin:', user_lookup[0][3])
		admin = user_lookup[0][3]
		if admin:
			results = sql.get_results_obj(date=date, order="date, name")
			return render_template('comments.html', results=results, date=date)
	print('returning a 404')
	return '',404


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
