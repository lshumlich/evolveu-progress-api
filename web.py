"""

"""
import datetime
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
import psycopg2
import json
import sql.sql as sql
import utils.dates

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
	print(uuid)
	id = request.args.get('id')
	user = request.args.get('user')
	email = request.args.get('email')
	startDate = request.args.get('startDate')

	# sql.insert_users(100,'Larry Shumlich', 'lshumlich@gmail.com', '2018-09-03')

	user_lookup = sql.get_user_by_uuid(uuid)
	if not user_lookup:
		print('returning a 404')
		return '',404

	print('inserting')
	sql.insert_users(int(id),user,email,startDate)

	print('returning')
	return "just playing"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
