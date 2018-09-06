"""

This is the sql utilities code for tracking learner progress. 
To execute this start at the application root directory. Enter the 
command below and it will present the options available, have fun.

python3 -m sql.sqlutil

"""

import sys
import os
import datetime
import traceback
import psycopg2
import uuid

import sql.sql
import sql.data

print("--- Starting", __file__)

# ------ 	Questions

def load_questions():
	""" 
	Load the questions into an internal array so we can use them later.
	"""
	order = 0

	results = []
	# columns = ('seq', 'code', 'question')

	for l in sql.data.questions.split('\n'):
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
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_questions)
		except psycopg2.ProgrammingError as e:
			print('Delete failed',sys.exc_info()[1])

		res = cur.execute(sql.sql.create_questions)
		questions = load_questions()
		count = 0
		for q in questions:
			res = cur.execute(sql.sql.insert_questions, q)
			count += 1
		print('--Questions Inserted:',count)

		conn.commit()
	except psycopg2.IntegrityError:
		print('*** Duplicate Key***')
		print('--1--',sys.exc_info()[1])
		raise
	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
		raise
	finally:
		cur.close()
		conn.close()


def questions():
	for q in sql.get_questions():
		print('-', q)

# ------ 	Users

def load_users():
	""" 
	Load the users into an internal array so we can use them later.
	"""

	results = []
	# columns = ('id', 'name', 'email', 'uuid')

	for l in sql.data.users.split('\n'):
		if l:
			# u = str(uuid.uuid4())
			# results.append(dict(zip(columns,[order] + l.split('@'))))
			results.append(l.split(',') + [str(uuid.uuid4())])

	return results

def init_users():
	""" 
	Load the users into the users database. It is important
	if there is existing data that user-id does not change. The user-uuid 
	is just used for security reasons.
	"""
	try:
		print("-- Init Users --");
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_users)
		except psycopg2.ProgrammingError as e:
			print('Delete failed',sys.exc_info()[1])

		res = cur.execute(sql.sql.create_users)
		users = load_users()
		count = 0
		for u in users:
			res = cur.execute(sql.sql.insert_users, u)
			count += 1
		print('--Users Inserted:',count)

		conn.commit()
	except psycopg2.IntegrityError:
		print('*** Duplicate Key***')
		print('--1--',sys.exc_info()[1])
		raise
	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
		raise
	finally:
		cur.close()
		conn.close()

def get_user_by_uuid():
	if len(sys.argv) < 2:
		print('What uuid would you like me to look for?')
	else:
		print(sql.get_user_by_uuid(sys.argv[2]))

	# print("just Playing", sys.argv)

# ------ 	Results

def init_results():
	""" 
	Create a results table.
	"""
	try:
		print("-- Init Results --");
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_results)
		except psycopg2.ProgrammingError as e:
			print('Delete failed',sys.exc_info()[1])

		res = cur.execute(sql.sql.create_results)

		conn.commit()
	except psycopg2.IntegrityError:
		print('*** Duplicate Key***')
		print('--1--',sys.exc_info()[1])
		return 1
	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
		return 1
	finally:
		cur.close()
		conn.close()
	return 0

def uuid_gen():
	for i in range(20):
		print(uuid.uuid4())

def connect():
	print("Connect String:",sql.get_connect_string())

# May not use this
def add_user():
	if len(sys.argv) < 2:
		pirnt('More parms are needed')

	url = sys.argv[2]
	uuid = sys.argv[3]

	print(url,uuid)


def test():
	"""
	Thursday - Tuesday - Enter for that date
	get to the Monday
	"""
	print("just Playing", sys.argv)
	today = datetime.date.today()
	print(today)
	print(today.weekday())

	d = datetime.date(2018,9,3)
	d += datetime.timedelta(days=5)

	print(d, d.weekday())


def usage():
	print("""
Pass one of the following options:

reload-questions 	: will reload the questions database
questions 			: will show the current questions loaded in teh database
reload-users 		: will reload the users database
get-user-by-uuid	: get a user based on uuid
init-results		: drop and create the results table
uuid 				: generate 20 uuid
connect 			: will show the connection string that will be used
add-user 			: add a new user
test				: just some play stuff
""")

options = {
	"reload-questions" : init_questions,
	"questions" : questions,
	"reload-users" : init_users,
	"get-user-by-uuid" : get_user_by_uuid,
	"init-results" : init_results,
	"uuid" : uuid_gen,
	"connect" : connect,
	"add-user" : add_user,
	"test" : test,
	"usage" : usage,
}

if __name__ == '__main__':
	option = sys.argv[1] if len(sys.argv) > 1 else 'usage'
	f = options.get(option, usage)
	f()
