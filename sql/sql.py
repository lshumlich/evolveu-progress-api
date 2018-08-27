import sys
import traceback
import psycopg2

connect = """
dbname=larry user=larry
"""

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

dummy = """
Create table questions (
	Id serial not null primary key,
	Secret varchar(100) not null,
	Name text unique not null
);
"""

def get_questions():
	""" 
	get the questions to be displayed on the screen.
	"""
	results = []
	try:
		print("-- Get Questions --");
		conn = psycopg2.connect(connect)
		cur = conn.cursor()
		res = cur.execute(select_questions)
		for r in cur:
			results.append(r[0])

	except:
		print('***We had a problem Huston...', sys.exc_info())
		traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
	finally:
		cur.close()
		conn.close()

	return results
