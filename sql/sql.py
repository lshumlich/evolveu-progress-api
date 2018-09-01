
import sys
import os
import datetime
import json
import traceback
import psycopg2
from psycopg2 import sql 
import utils.dates

default_connect = """
dbname=larry user=larry
"""

# --- Questions

drop_questions = """
Drop table questions;
"""

create_questions = """
Create table questions (
	Seq integer not null,
	Code varChar(10) not null unique primary key,
	Question text not null
);
"""

insert_questions = """
insert into questions (seq, code, question) values(%s, %s, %s)
"""

select_questions = """
select question from questions order by seq;
"""

select_questions2 = """
select code,question from questions order by seq;
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
	start_date date not null
);
"""
# f8862239-ec71-43b9-b9a9-5cf918040f08

insert_users = """
insert into users (id, name, email, start_date, uuid) values(%s, %s, %s, %s, %s)
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

get_results_by_student_date_string = """
select result, going_well, issues, what_to_try
	from results
	where student = %s and date = %s;
"""

def get_connect_string():
	return os.environ.get('DATABASE_URL', default_connect)

def get_questions():
	return select(select_questions,[])

def get_questions2():
	results = []
	columns = ('code', 'question')
	questions = select(select_questions2,[])
	for q in questions:
		results.append(dict(zip(columns,q)))
	return results

get_users_string = """
select id, name, email, uuid, start_date from users;
"""

def get_users():
	return select(get_users_string,None)


select_user_by_ggid = """
select id, name, start_date from users where uuid = %s;
"""

def get_user_by_uuid(ggid):
	return select(select_user_by_ggid,[ggid])

def insert_results(data):
	return sql_util(insert_results_string, data)

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
