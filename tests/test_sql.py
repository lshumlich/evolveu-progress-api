"""
To run the tests from the app root directory

PYTHONPATH=. pytest

--- Select only tests that have questions in the test name and don't hide the output
PYTHONPATH=. pytest -k questions -s
PYTHONPATH=. pytest -s
PYTHONPATH=. pytest tests/test_sql.py -k _obj -s


"""
import unittest
import datetime
import sql.sql
import sql.sqlutil
import things.results

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

	def test_update_results_text(self):
		# Big assumptions here which is bad the student already exists
		going_well = 'Everything just everything'
		issues = 'We have sooo many issues'
		what_to_try = 'Lets try it all'
		sql.sql.update_result_text_student_date(1, '2018-09-03', 'going_well', going_well)
		sql.sql.update_result_text_student_date(1, '2018-09-03', 'issues', issues)
		sql.sql.update_result_text_student_date(1, '2018-09-03', 'what_to_try', what_to_try)
		result = sql.sql.get_results_by_student_date(1, '2018-09-03')
		self.assertEqual(going_well, result[0][1])
		self.assertEqual(issues, result[0][2])
		self.assertEqual(what_to_try, result[0][3])

	def test_update_results(self):
		# Big assumptions here which is bad the student already exists
		value = 3
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'logic', value)
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'sql', value)
		r = sql.sql.get_result_object_by_student_date(1, '2018-09-03')
		self.assertEqual(r[0]['logic'], value)
		self.assertEqual(r[0]['sql'], value)

		value = 7
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'logic', value)
		sql.sql.update_result_by_student_date(1, '2018-09-03', 'sql', value)
		r = sql.sql.get_result_object_by_student_date(1, '2018-09-03')
		self.assertEqual(r[0]['logic'], value)
		self.assertEqual(r[0]['sql'], value)

	def test_users(self):
		sql.sqlutil.init_users()
		users = sql.sql.get_users()
		self.assertEqual(2, len(users))

		print('The users are:', users)

		uuid = users[0].uuid
		email = users[0].email

		user = sql.sql.get_user_by_email("bad")
		self.assertIsNone(user)

		user = sql.sql.get_user_by_email(email)
		self.assertEqual(user.uuid, uuid)
		self.assertEqual(user.email, email)

		user = sql.sql.get_user_by_uuid('bad')
		self.assertIsNone(user)

		user = sql.sql.get_user_by_uuid(uuid)
		self.assertEqual(user.uuid, uuid)
		self.assertEqual(user.email, email)


	def test_questions(self):
		sql.sqlutil.init_questions()
		questions = sql.sql.get_questions()
		self.assertTrue(len(questions) > 1)

	def test_get_results_obj(self):
		self.create_test_data1()

		result = sql.sql.get_results_obj()
		self.assertEqual(2, len(result))

		self.assertEqual(3, result[0].total())

		result = sql.sql.get_results_obj(date='2017-01-01')
		self.assertEqual(0, len(result))

		result = sql.sql.get_results_obj(date='2018-09-03')
		self.assertEqual(1, len(result))
		self.assertEqual(datetime.date(2018, 9, 3), result[0].date)

		result = sql.sql.get_results_obj(date='2018-09-10')
		self.assertEqual(1, len(result))
		self.assertEqual(datetime.date(2018, 9, 10), result[0].date)

		result = sql.sql.get_results_obj(student=1000)
		self.assertEqual(1, len(result))
		self.assertEqual("Larry Shumlich", result[0].student)

		result = sql.sql.get_results_obj(student=1001)
		self.assertEqual(1, len(result))
		self.assertEqual("Lorraine Shumlich", result[0].student)
		self.assertEqual("Lorraine", result[0].first_name())


		result = sql.sql.get_results_obj(order="name")
		self.assertEqual(2, len(result))
		self.assertEqual("Larry Shumlich", result[0].student)
		self.assertEqual("Lorraine Shumlich", result[1].student)

		result = sql.sql.get_results_obj(order="date")
		self.assertEqual(2, len(result))
		self.assertEqual(datetime.date(2018, 9, 3), result[0].date)
		self.assertEqual(datetime.date(2018, 9, 10), result[1].date)

		result = sql.sql.get_results_obj(order="date, name")

		result = sql.sql.get_results_obj(date='2018-09-10', student=1001)

	def test_get_question_results(self):
		self.create_test_data1()

		results = sql.sql.get_results_obj(order = "date")
		self.assertEqual([{'axis':'logic','value':2},
						  {'axis':'whatever','value':0}
						 ], 
						 results[0].get_question_results([{'code':'logic'},
														  {'code':'whatever'}]))

		sql.sqlutil.init_questions()
		questions = sql.sql.get_questions()
		# Just make sure it runs
		results[0].get_question_results(questions)

	def test_get_prev_result(self):
		self.create_test_data1()
		self.create_test_data2()
		results = sql.sql.get_prev_results_obj(level=0, date="2018-09-10", order = "date")
		self.assertIsNotNone(results[0].get_prev_result(0))
		self.assertIsNone(results[0].get_prev_result(1))

		results = sql.sql.get_prev_results_obj(level=1, date="2018-09-10", order = "date")
		self.assertIsNotNone(results[0].get_prev_result(0))
		self.assertIsNotNone(results[0].get_prev_result(1))
		self.assertIsNone(results[0].get_prev_result(2))

		results = sql.sql.get_prev_results_obj(level=2, date="2018-09-10", order = "date")
		self.assertEqual(2, len(results))
		self.assertIsNotNone(results[0].get_prev_result(0))
		self.assertIsNotNone(results[0].get_prev_result(1))
		self.assertIsNone(results[0].get_prev_result(2))

		# Only looking for 1 student
		results = sql.sql.get_prev_results_obj(level=2, date="2018-09-10", order = "date", student=1000)
		self.assertEqual(1, len(results))

	def test_get_missing_for_date(self):
		self.create_test_data1()
		results = sql.sql.get_missing_for_date("2018-09-11")
		self.assertEqual(1, len(results))
		self.assertEqual('Lorraine Shumlich', results[0].name)

	def create_test_data1(self):
		sql.sqlutil.init_users()
		self.assertEqual(0, sql.sqlutil.init_results())

		result = '{"sql":1,"logic":2}'
		s = [1001,'2018-09-10',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)

		s = [1000,'2018-09-03',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)

	def create_test_data2(self):
		result = '{"sql":1,"logic":1}'
		s = [1001,'2018-09-03',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)

		result = '{"sql":3,"logic":3}'
		s = [1000,'2018-09-10',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)
