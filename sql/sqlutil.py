
import sys
import os
import traceback
import psycopg2

import data
import sql

print("--- Starting", __file__)

def load_questions():
	""" 
	Load the questions into an internal array so we can use them later.
	"""
	order = 0

	results = []
	columns = ('seq', 'code', 'question')

	for l in data.questions.split('\n'):
		if l:
			order += 10
			# results.append(dict(zip(columns,[order] + l.split('@'))))
			results.append([order] + l.split('@'))

	return results

def init_questions():
	""" 
	Load the questions into the questions database. It is important
	if there is existing data that the question-code does not change. All the weekly
	data is stored based on the code.
	"""
	try:
		print("-- Init Questions --");
		conn = psycopg2.connect(sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.drop_questions)
		except psycopg2.ProgrammingError as e:
			print('Delete failed',sys.exc_info()[1])

		res = cur.execute(sql.create_questions)
		questions = load_questions()
		count = 0
		for q in questions:
			res = cur.execute(sql.insert_questions, q)
			count += 1
		print('--Questions Inserted:',count)

		conn.commit()
	except psycopg2.IntegrityError:
		print('*** Duplicate Key***')
		print('--1--',sys.exc_info()[1])
	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
	finally:
		cur.close()
		conn.close()


def questions():
	for q in sql.get_questions():
		print('-', q)

def connect():
	print("Connect String:",sql.get_connect_string())

def usage():
	print("""
Pass one of the following options:

reload-questions : will reload the questions database
questions : will show the current questions loaded in teh database
connect : will show the connection string that will be used

""")

options = {
	"reload-questions" : init_questions,
	"questions" : questions,
	"connect" : connect,
	"usage" : usage,
}

option = sys.argv[1] if len(sys.argv) > 1 else 'usage'
f = options.get(option, usage)
f()
