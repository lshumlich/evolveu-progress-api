
import sys
import os
import datetime
import json
import traceback
import uuid

import psycopg2
from psycopg2 import sql 
import utils.dates
import things.results

# --- Questions

drop_questions = """
Drop table questions;
"""

create_questions = """
Create table questions (
	Seq integer not null,
	Code varChar(16) not null unique primary key,
	Question text not null
);
"""

insert_questions = """
insert into questions (seq, code, question) values(%s, %s, %s)
"""

# --- Users

drop_users = """
Drop table users;
"""

create_users = """
Create table users (
	id integer not null unique primary key,
	name varChar(50) not null,
	email varChar(50) not null,
	uuid varChar(36) not null,
	start_date date not null,
	admin boolean not null
);
"""

# --- Results

drop_results = """
Drop table results;
"""

create_results = """
Create table results (
	Id serial not null primary key,
	student integer not null,
	date date not null,
	result text not null,
	going_well text,
	issues text,
	what_to_try text
);
"""

insert_results_string = """
insert into 
	results (student, date, result, going_well, issues, what_to_try) 
	values  (%s, %s, %s, %s, %s, %s) returning id;
"""

default_connect = """
dbname=larry user=larry
"""

def get_connect_string():
	return os.environ.get('DATABASE_URL', default_connect)


select_questions = """
select code,question from questions order by seq;
"""

def get_questions():
	results = []
	columns = ('code', 'question')
	questions = select(select_questions,[])
	for q in questions:
		results.append(dict(zip(columns,q)))
	return results

# f8862239-ec71-43b9-b9a9-5cf918040f08 (Sample of a uuid)

insert_users_string = """
insert into users (id, name, email, start_date, admin, uuid) values(%s, %s, %s, %s, %s, %s)
"""

def insert_users(id, name, email, start_date, admin):
	""" 
	Insert a single user into the users table.
	"""
	return sql_util(insert_users_string, [id, name, email, start_date, admin, str(uuid.uuid4())])

get_users_string = """
select id, name, email, start_date, admin, uuid from users;
"""

def get_users():
	return select(get_users_string,None)


select_user_by_ggid = """
select id, name, start_date, admin from users where uuid = %s;
"""

def get_user_by_uuid(ggid):
	return select(select_user_by_ggid,[ggid])

def insert_results(data):
	return sql_util(insert_results_string, data)

get_results_by_student_date_string = """
select result, going_well, issues, what_to_try
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
		new_r = [r[0][0], '', '', '']
		insert_results([student, date] + new_r)
		return [new_r]
	# insert a empty one
	new_r = ['{}', '', '', '']
	insert_results([student, date] + new_r)
	return [new_r]

def get_result_object_by_student_date(student_id, date):
	result = get_results_by_student_date(student_id, date)
	return json.loads(result[0][0]),result[0][1],result[0][2],result[0][3]


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
# from now on starting using this generic object friendly
# function
#

get_results_obj_string = """
select date, name, result, going_well, issues, what_to_try
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
		sql_string = sql_string + f"date = '{date}' "

	if student:
		sql_string = sql_string + f'student = {student} '

	if order:
		order_by = ' order by ' + order
	else:
		order_by = ''

	sql_string = get_results_obj_string + sql_string + order_by + ';'
	# print('----', sql_string)
	sql_results = select(sql_string, [])
	res = []
	for r in sql_results:
		res.append(things.results.Result(r[0], r[1],r[2],r[3],r[4],r[5]))

	return res

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
