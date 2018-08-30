"""
To run the tests from the app root directory

PYTHONPATH=. pytest

--- Select only tests that have questions in the test name and don't hide the output
PYTHONPATH=. pytest -k questions -s
PYTHONPATH=. pytest -s

"""
import unittest
import datetime
import sql.sql
import sql.sqlutil

class TestSql(unittest.TestCase):

	def test_results(self):
		self.assertEqual(0, sql.sqlutil.init_results())

		result = '{"sql":1,"logic":2}'
		s = [1,'2018-09-03',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)

		r = sql.sql.get_results_by_student_date(1, '2018-09-03')
		# what we inserted should be = retrieved
		self.assertEqual(1, len(r))
		self.assertEqual(result, r[0][0])

		# This tests the copy forward functionality. If no record exists for a week 
		# (which in this case it should not) it will automaticly copy the results forward.
		r = sql.sql.get_results_by_student_date(1, '2018-09-10')
		self.assertEqual(1, len(r))
		self.assertEqual(result, r[0][0])
		self.assertEqual('', r[0][1])
		self.assertEqual('', r[0][2])
		self.assertEqual('', r[0][3])

		# This tests the copy forward functionality is not to active and only 
		# copies forward one week.
		r = sql.sql.get_results_by_student_date(1, '2018-09-24')
		self.assertEqual(1, len(r))
		self.assertEqual('{}', r[0][0])
		self.assertEqual('', r[0][1])
		self.assertEqual('', r[0][2])
		self.assertEqual('', r[0][3])

	def test_update_going_well(self):
		sql.sql.update_going_well_by_student_date(1, '2018-09-03', 'Its going sooo well')

	def test_update_results(self):
		# Big assumptions here which is bad the student already exists
		value = 3
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'logic', value)
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'sql', value)
		r = sql.sql.get_result_object_by_student_date(1, '2018-09-03')
		self.assertEqual(r['logic'], value)
		self.assertEqual(r['sql'], value)

		value = 7
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'logic', value)
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'sql', value)
		r = sql.sql.get_result_object_by_student_date(1, '2018-09-03')
		self.assertEqual(r['logic'], value)
		self.assertEqual(r['sql'], value)



	def test_users(self):
		sql.sqlutil.init_users()
		users,cols = sql.sql.get_users()
		print(users)
		print(cols)
		for u in users:
			print(u[cols.id])
		# self.assertTrue(len(users) > 1)

	def test_questions(self):
		sql.sqlutil.init_questions()
		questions = sql.sql.get_questions2()
		self.assertTrue(len(questions) > 1)

	def test_play(self):
		print('Hello')
		m = {'one':1, 'two':2, 'three':'three'}
		o = ('one':1, 'two':2, 'three':'three')
		print(m)
		print(o)
		print(m['one'])
		print(m.one)
		print(type(m))