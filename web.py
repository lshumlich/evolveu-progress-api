
from flask import Flask
from flask import jsonify
from flask_cors import CORS
import psycopg2
import json
import sql.sql as sql


print('Hello World.')

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
	return "Hello World!1"


@app.route("/questions")
def questions():
	return jsonify(sql.get_questions())

@app.route("/info/<name>/<date>")
def info(name=None,date=None):
	s = f'Hello World {name} {date}'
	return s

def playWithDb():
	conn = psycopg2.connect("dbname=larry user=larry")
	cur = conn.cursor()
	r1 = cur.execute("select * from users;")
	# r1 = cur.execute("select name,age, age, score from users;")
	# print('conn', conn)
	# print('cur', cur)
	# r2 = cur.fetchone()
	results = []
	columns = ('name', 'age', 'birthday', 'score')
	for r in cur:
		results.append(dict(zip(columns,r)))
		print(r)
		print(r[0])
		print(r[1])
		print(r[2])
		print(r[3])

	# print(r1)
	# print(r2)
	print (json.dumps(results, indent=3, default=str))

	cur.close()
	conn.close()

# playWithDb();

# print('sql connect:',sql.connect)

# print(sql.get_questions())

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
