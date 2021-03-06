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

import sql.sql
import sql.data

print("--- Starting", __file__)

# ------ 	Questions

def xxx_load_questions():
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
	do nothing right now.
	"""
	None 

def questions():
	for q in sql.sql.get_questions():
		print('-', q)

def comps():
	for q in sql.sql.get_comps():
		print('-', q)

# ------ 	Users

def init_users():
	""" 
	Delete the table (if it exists) and create a new users table. Insert one user so
	that that user's UUID can be used to add additional users. The user-uuid 
	is just used for security reasons.
	"""
	try:
		# print("-- Init Users --");
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_users)
		except:
			print('Delete failed',sys.exc_info()[1])
			conn.rollback()

		res = cur.execute(sql.sql.create_users)

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

	sql.sql.insert_users('Larry Shumlich', 'lshumlich@gmail.com', 'FSD0', '2019-09-30', True)
	sql.sql.insert_users('Lorraine Shumlich', 'lmshumlich@gmail.com', 'FSD0', '2019-09-30', False)
	# print('--Users Inserted: 2')

def get_user_by_uuid():
	if len(sys.argv) < 2:
		print('What uuid would you like me to look for?')
	else:
		print(sql.get_user_by_uuid(sys.argv[2]))

	# print("just Playing", sys.argv)

# ------ 	session

def init_session():
	""" 
	Delete the table (if it exists) and create a new session table.
	"""
	try:
		# print("-- Init Session --");
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_session)
		except:
			print('Delete failed',sys.exc_info()[1])
			conn.rollback()

		res = cur.execute(sql.sql.create_session)

		conn.commit()
	except psycopg2.IntegrityError:
		print('--1--',sys.exc_info()[1])
		raise
	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
		raise
	finally:
		cur.close()
		conn.close()

# ------ 	Results

def init_results():
	""" 
	Create a results table.
	"""
	try:
		# print("-- Init Results --");
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_results)
		except:
			print('Delete failed',sys.exc_info()[1])
			conn.rollback()

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

# ------ 	Options

def init_options():
	""" 
	Delete the table (if it exists) and create a new options table. Insert a little data.
	"""
	try:
		# print("-- Init Options --");
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_options)
		except:
			print('Delete failed',sys.exc_info()[1])
			conn.rollback()

		res = cur.execute(sql.sql.create_options)

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

	sql.sql.insert_options('questions',sql.data.questions)
	sql.sql.insert_options('comps',sql.data.comps)
	# sql.sql.insert_options('Lorraine Shumlich', 'lmshumlich@gmail.com', 'FSD0', '2019-09-30', False)
	# print('--Users Inserted: 2')
	return 0


# ------ 	Options

def init_compdates():
	""" 
	Delete the table (if it exists) and create a new one.
	"""
	try:
		# print("-- Init Options --");
		conn = psycopg2.connect(sql.sql.get_connect_string(), sslmode='require')
		cur = conn.cursor()
		try:
			res = cur.execute(sql.sql.drop_compdates)
		except:
			print('Delete failed',sys.exc_info()[1])
			conn.rollback()

		res = cur.execute(sql.sql.create_compdates)

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

	return 0

def connect():
	print("Connect String:", sql.sql.get_connect_string())

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

init-users          : drop and create the users table and add two users
init-results        : drop and create the results table
init-session		: drop and create the session table
init-options		: drop and create the options table
init-compdates      : drop and create the compdates table
---
questions           : will show the current questions loaded in the database
comps               : will show the current competencies loaded in the database
get-user-by-uuid    : get a user based on uuid
connect             : will show the connection string that will be used
test                : just some play stuff
""")

help_options = {
	"init-users" : init_users,
	"init-results" : init_results,
	"init-session" : init_session,
	"init-options" : init_options,
	"init-compdates" : init_compdates,
	"questions" : questions,
	"comps" : comps,
	"get-user-by-uuid" : get_user_by_uuid,
	"connect" : connect,
	"test" : test,
	"usage" : usage,
}

if __name__ == '__main__':
	option = sys.argv[1] if len(sys.argv) > 1 else 'usage'
	f = help_options.get(option, usage)
	f()
