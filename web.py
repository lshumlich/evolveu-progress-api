
from flask import Flask
from flask import jsonify
from flask_cors import CORS
import psycopg2
import json
import sql.sql as sql

print("--- Starting", __file__)

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
	return "Hello World!1 from EvolveU Evaluation"


@app.route("/questions")
def questions():
	return jsonify(sql.get_questions())

@app.route("/info/<name>/<date>")
def info(name=None,date=None):
	s = f'Hello World {name} {date}'
	return s


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
