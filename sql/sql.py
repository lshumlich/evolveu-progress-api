
import sys
import os
import datetime
import json
import traceback
import uuid

import psycopg2
from psycopg2 import sql 

import sql.data
import utils.dates
import things.results
import things.user
import things.session
from things.struc import Struc 

drop_users = """
Drop table users;
"""

create_users = """
Create table users (
	id serial not null primary key,
	name varChar(50) not null,
	email varChar(50) not null unique,
	uuid varChar(36) not null,
	start_date date,
	admin boolean not null
);
"""

# --- Results

drop_results = """
Drop table results;
"""

create_results = """
Create table results (
	id serial not null primary key,
	student integer not null,
	date date not null,
	result text not null,
	going_well text,
	issues text,
	what_to_try text,
	exercise text,
	industryproj boolean,
	predcompdate date
);
"""

# --- Session

drop_session = """
Drop table session;
"""

create_session = """
Create table session (
	id varchar not null primary key,
	email varChar(50) not null,
	date date not null
);
"""

default_connect = """
dbname=larry user=larry
"""

def get_connect_string():
	return os.environ.get('DATABASE_URL', default_connect)

select_session = """
select id, email, date from session where id = %s;
"""

def get_session(id):
	sql_results = select(select_session,[id])
	if sql_results:
		r = sql_results[0]
		return things.session.Session(r[0], r[1],r[2])
	return None

insert_session_string = """
insert into session (id, email, date) values(%s, %s, %s)
"""

def insert_session(id, email):
	""" 
	Insert a session user into the session table.
	"""
	dt = str(datetime.date.today())
	return sql_util(insert_session_string, [id, email, dt])

delete_session_string = """
delete from session where id = %s
"""

def delete_session(id):
	""" 
	delete a session from the session table.
	"""
	sql_util(delete_session_string, [id])

delete_all_sessions_string = """
delete from session
"""

def delete_all_sessions():
	""" 
	delete all sessions from the session table.
	"""
	sql_util(delete_all_sessions_string, [])

def get_questions(qtype=None):
	results = []
	columns = ('type', 'code', 'question')
	for l in sql.data.questions.split('\n'):
		if l:
			a = l.split('@')
			if (not qtype or qtype == a[0]):
				results.append(dict(zip(columns, l.split('@'))))

	return results

# f8862239-ec71-43b9-b9a9-5cf918040f08 (Sample of a uuid)

insert_users_string = """
insert into users (name, email, start_date, admin, uuid) values(%s, %s, %s, %s, %s)
"""

def insert_users(name, email, start_date, admin):
	""" 
	Insert a single user into the users table.
	"""
	return sql_util(insert_users_string, [name, email, start_date, admin, str(uuid.uuid4())])

get_users_string = """
select id, name, email, uuid, start_date, admin from users;
"""

def get_users():
	sql_results = select(get_users_string,None)
	res = []
	for r in sql_results:
		res.append(things.user.User(r[0], r[1],r[2],r[3],r[4],r[5]))

	return res

select_user_by_ggid = """
select id, name, email, uuid, start_date, admin from users where uuid = %s;
"""

def get_user_by_uuid(ggid):
	sql_results = select(select_user_by_ggid,[ggid])
	if sql_results:
		r = sql_results[0]
		return things.user.User(r[0], r[1],r[2],r[3],r[4],r[5])
	return None

select_user_by_email = """
select id, name, email, uuid, start_date, admin from users where email = %s;
"""

def get_user_by_email(email):
	sql_results = select(select_user_by_email,[email])
	if sql_results:
		r = sql_results[0]
		return things.user.User(r[0], r[1],r[2],r[3],r[4],r[5])
	return None

insert_results_string = """
insert into 
	results (student, date, result, going_well, issues, what_to_try, exercise, industryproj, predcompdate) 
	values  (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning id;
"""

def insert_results(data):
	return sql_util(insert_results_string, data)

get_results_by_student_date_string = """
select result, going_well, issues, what_to_try, exercise, industryproj, predcompdate
	from results
	where student = %s and date = %s;
"""

def get_results_by_student_date(student, date):
	r = select(get_results_by_student_date_string, [student, date])
	if r: return r

	# Now check to see if there is a result last week and carry if forward if there is
	last_monday = utils.dates.last_monday(utils.dates.to_date(date))
	r = select(get_results_by_student_date_string, [student, str(last_monday)])
	if r:
		new_r = [r[0][0], '', '', '', r[0][4], r[0][5], r[0][6]]
		insert_results([student, date] + new_r)
		return [new_r]
	# insert an empty one
	# new_r = ['{}', '', '', '', '', 'false', '2019-01-01']
	new_r = ['{}', '', '', '', '', 'false', datetime.datetime.now().date()]
	insert_results([student, date] + new_r)
	return [new_r]

def get_result_object_by_student_date(student_id, date):
	result = get_results_by_student_date(student_id, date)
	# print(result)
	return json.loads(result[0][0]),result[0][1],result[0][2],result[0][3],result[0][4],result[0][5],result[0][6]


get_results_string = """
select date, name, result, going_well, issues, what_to_try
	from results, users
	where
	student = users.id
	order by date, name;
"""

def get_results():
	r = select(get_results_string, [])
	return r

#
# from now on start using this generic object friendly
# function
#

get_results_obj_string = """
select date, student, name, result, going_well, issues, what_to_try, exercise, industryproj, predcompdate
	from results, users
	where
	student = users.id
"""

def get_results_obj(date=None, student=None, order=None):
	if date or student:
		sql_string = ' and '
	else:
		sql_string = ''

	if date:
		sql_string += f"date = '{date}' "

	if date and student:
		sql_string += ' and '

	if student:
		sql_string += f'student = {student} '

	if order:
		order_by = ' order by ' + order
	else:
		order_by = ''

	sql_string = get_results_obj_string + sql_string + order_by + ';'
	# print('----', sql_string)
	sql_results = select(sql_string, [])
	res = []
	for r in sql_results:
		# print('rrrr', r)
		res.append(things.results.Result(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9]))

	return res

def get_prev_results_obj(level=0, date=None, student=None, order=None):
	results = get_results_obj(date=date, student=student, order=order)
	if level:
		students = {}
		for r in results:
			students[r.student_id] = r
		search_date = date
		for i in range(level):

			search_date = str(utils.dates.last_monday(utils.dates.to_date(search_date)))
			next_results = get_results_obj(date=search_date, student=student, order=order)
			for n in next_results:
				if n.student_id in students:
					students[n.student_id].set_prev_result(i, n)
		
	return results

get_missing_for_date_string = """
select name from users where not admin and users.id not in
	(select results.student from results where results.date = %s);
"""

def get_missing_for_date(date):
	values = []
	results = select(get_missing_for_date_string,[date])
	for r in results:
		struc = Struc()
		struc.name = r[0]
		values.append(struc)
	return values


update_result_by_student_date_string = """
update results
	set result = %s
	where student = %s and date = %s;
"""

def update_result_by_student_date(student_id, date, code, score):
	results = get_result_object_by_student_date(student_id, date)
	scores = results[0]
	scores[code] = score
	sql_util(update_result_by_student_date_string,[json.dumps(scores), student_id, date])


def update_result_text_student_date(student_id, date, attribute, value):
	sql = \
f"""
update results
	set {attribute} = %s
	where student = %s and date = %s;
"""
	sql_util(sql,[value, student_id, date])

# ----- general utilitis

def select(sql, parms):
	""" 
	Execute standard sql statements.
	"""
	results = []
	try:
		conn = psycopg2.connect(get_connect_string(), sslmode='require')
		cur = conn.cursor()
		res = cur.execute(sql, parms)
		for r in cur:
			results.append(r)

	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
		raise
	finally:
		cur.close()
		conn.close()

	return results

def sql_util(sql, parms):
	""" 
	Run general maintaince statements.
	"""
	results = []
	try:
		conn = psycopg2.connect(get_connect_string(), sslmode='require')
		cur = conn.cursor()
		res = cur.execute(sql, parms)
		# This may return the id of an inserted row
		# for r in cur:
		# 	results.append(r)
		conn.commit()

	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
		raise
	finally:
		cur.close()
		conn.close()

	return results
