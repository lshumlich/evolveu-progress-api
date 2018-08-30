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

@app.route("/questions2")
def questions2():
	return jsonify(sql.get_questions2())

@app.route("/results/<uuid>/")
@app.route("/results/<uuid>/<date>")
def results(uuid=None, date=None):

	user = sql.get_user_by_uuid(uuid)
	if not user:
		return '',404
	id = user[0][0]

	this_monday = utils.dates.my_monday(datetime.datetime.now().date())

	# Monday is the day the user wants to see
	if not date:
		monday = this_monday
	else:
		monday = utils.dates.to_date(date)

	next_monday = utils.dates.next_monday(monday)
	last_monday = utils.dates.last_monday(monday)

	if next_monday > monday:
		next_monday = ''

	results = sql.get_result_object_by_student_date(id, str(monday))

	return jsonify({'results':results, 'last_monday': str(last_monday), 'this_monday': str(monday), 'next_monday': str(next_monday)})

@app.route("/update", methods = ['POST'])
def update():
	content = request.get_json()
	print(content)

	user = sql.get_user_by_uuid(content['uuid'])
	if not user:
		return '',404
	id = user[0][0]

	row = sql.get_results_by_student_date(id, content['date'])


	if content['type'] == 'score':
		sql.update_result_by_student_date(id, content['date'], content['code'], int(content['value']))
	else:
		print('We should update the text:',content['code'], content['value'])

	return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
