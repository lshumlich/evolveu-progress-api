"""
To run the tests from the app root directory

PYTHONPATH=. pytest

--- Select only tests that have questions in the test name and don't hide the output
PYTHONPATH=. pytest -k questions -s
PYTHONPATH=. pytest -s
PYTHONPATH=. pytest tests/test_results.py -s -k _res


"""
import unittest
import datetime
import sql.sql
import sql.sqlutil
import things.results

class TestResults(unittest.TestCase):

	def test_results(self):
		# def __init__(self, date, student_id, student, result, going_well, issues, what_to_try):
		result_09_03 = things.results.Result('2018-09-03', 1000, 'Larry Shumlich', 
										{'Logic':0,'Basic DS':1},
										'going well', 'real issues', 'try new stuff', '100')
		result_08_27 = things.results.Result('2018-08-27', 1000, 'Larry Shumlich', 
										{'Logic':2,'Basic DS':0},
										'going well', 'real issues', 'try new stuff', '100')
		result_08_20 = things.results.Result('2018-08-20', 1000, 'Larry Shumlich', 
										{'Logic':0,'Basic DS':3},
										'going well', 'real issues', 'try new stuff', '100')
		result_08_13 = things.results.Result('2018-08-13', 1000, 'Larry Shumlich', 
										{'Logic':4,'Basic DS':0},
										'going well', 'real issues', 'try new stuff', '100')
		result_08_06 = things.results.Result('2018-08-06', 1000, 'Larry Shumlich', 
										{'Logic':5,'Basic DS':5},
										'going well', 'real issues', 'try new stuff', '100')

		self.assertEqual('Larry Shumlich', result_09_03.student);
		self.assertEqual('Larry', result_09_03.first_name());
		self.assertEqual('Larry_1000', result_09_03.field_name());

		self.assertEqual('2018-09-03', result_09_03.get_prev_result(0).date)
		self.assertIsNone(result_09_03.get_prev_result(1))


		result_09_03.set_prev_result(0, result_08_27)
		self.assertEqual('2018-09-03', result_09_03.get_prev_result(0).date)
		self.assertEqual('2018-08-27', result_09_03.get_prev_result(1).date)
		self.assertIsNone(result_09_03.get_prev_result(2))

		result_09_03.set_prev_result(1, result_08_20)
		self.assertEqual('2018-09-03', result_09_03.get_prev_result(0).date)
		self.assertEqual('2018-08-27', result_09_03.get_prev_result(1).date)
		self.assertEqual('2018-08-20', result_09_03.get_prev_result(2).date)
		self.assertIsNone(result_09_03.get_prev_result(3))


		result_09_03.set_prev_result(2, result_08_13)
		self.assertEqual('2018-09-03', result_09_03.get_prev_result(0).date)
		self.assertEqual('2018-08-27', result_09_03.get_prev_result(1).date)
		self.assertEqual('2018-08-20', result_09_03.get_prev_result(2).date)
		self.assertEqual('2018-08-13', result_09_03.get_prev_result(3).date)
		self.assertIsNone(result_09_03.get_prev_result(4))

		result_09_03.set_prev_result(3, result_08_06)
		self.assertEqual('2018-09-03', result_09_03.get_prev_result(0).date)
		self.assertEqual('2018-08-27', result_09_03.get_prev_result(1).date)
		self.assertEqual('2018-08-20', result_09_03.get_prev_result(2).date)
		self.assertEqual('2018-08-13', result_09_03.get_prev_result(3).date)
		self.assertEqual('2018-08-06', result_09_03.get_prev_result(4).date)
		self.assertIsNone(result_09_03.get_prev_result(5))

		self.assertEqual(1, result_09_03.get_prev_total(0))
		self.assertEqual(2, result_09_03.get_prev_total(1))
		self.assertEqual(3, result_09_03.get_prev_total(2))
		self.assertEqual(4, result_09_03.get_prev_total(3))
		self.assertEqual(10, result_09_03.get_prev_total(4))
		self.assertEqual(0, result_09_03.get_prev_total(5))

		questions = [{'code':'Logic'}, {'code':'Asdf'}, {'code':'Basic DS'}]

		self.assertEqual([{'axis': 'Logic', 'value': 0}, 
						  {'axis': 'Asdf', 'value': 0}, 
						  {'axis': 'Basic DS', 'value': 1}],
						 result_09_03.get_prev_question_results(0, questions))
		
		self.assertEqual([{'axis': 'Logic', 'value': 2}, 
						  {'axis': 'Asdf', 'value': 0}, 
						  {'axis': 'Basic DS', 'value': 0}],
						 result_09_03.get_prev_question_results(1, questions))
		
		self.assertEqual([{'axis': 'Logic', 'value': 0}, 
						  {'axis': 'Asdf', 'value': 0}, 
						  {'axis': 'Basic DS', 'value': 3}],
						 result_09_03.get_prev_question_results(2, questions))

	def test_prev_total_for_questions(self):
		# def __init__(self, date, student_id, student, result, going_well, issues, what_to_try):
		result_2019_03_18 = things.results.Result('2019-03-18', 1000, 'Larry Shumlich', 
										{'Logic':2,'JS':3, 'PY':4},
										'going well', 'real issues', 'try new stuff', '100')

		self.assertEqual(9, result_2019_03_18.get_prev_total(0))

		questions = [{'code':'Logic'}, {'code':'Asdf'}, {'code':'JS'}]
		self.assertEqual(5, 
			result_2019_03_18.total_for_questions(questions))
		self.assertEqual(5, 
			result_2019_03_18.get_prev_total_for_questions(0, questions))

