"""

PYTHONPATH=. pytest tests/test_weekly_report.py -k weekly -s

"""

import datetime
import unittest

import sql.sqlutil
import sql.sql
import utils.weekly_report

class TestWeeklyReport(unittest.TestCase):

	def test_weekly_report(self):

		sql.sqlutil.init_users()
		self.assertEqual(0, sql.sqlutil.init_results())

		result = '{"SQL":1,"JS Logic":2}'
		s = [1,'2018-09-03',result,'all is well', 'no issues', 'try harder next week', '100', 'true', datetime.date(2019,5,30)]
		sql.sql.insert_results(s)
		result = '{"SQL":1,"JS Logic":3}'
		s = [1,'2018-09-10',result,'all is well', 'no issues', 'try harder next week', '100', 'true', datetime.date(2019,5,30)]
		sql.sql.insert_results(s)
		result = '{"SQL":1,"JS Logic":4}'
		s = [1,'2018-09-17',result,'all is well', 'no issues', 'try harder next week', '100', 'true', datetime.date(2019,5,30)]
		sql.sql.insert_results(s)

		report = utils.weekly_report.create_weekly_report('2018-09-03', '2018-09-17')
		self.assertEqual(2, report.week_number)
		self.assertEqual(1, len(report.results))
		self.assertEqual(1, len(report.missing))

		# print("one person:", report.class_progress[1])
		# print("one person:", report.results[0])
		# based on the number of ratings
		self.assertEqual('Target',report.class_progress[0].name)
		self.assertEqual([0,8,17], report.class_progress[0].weekly)

		self.assertEqual('Larry Shumlich',report.class_progress[1].name)
		self.assertEqual([3,4,5], report.class_progress[1].weekly)

		# based on the number of ratings
		self.assertEqual([{'week':0, 'score':0},{'week':1, 'score':8},{'week':2, 'score':17}],
						report.class_progress[0].get_weekly_results())
		self.assertEqual([{'week':0, 'score':3},{'week':1, 'score':4},{'week':2, 'score':5}],
						report.class_progress[1].get_weekly_results())

		# based on the number of ratings
		self.assertEqual(17,
						report.class_progress[0].get_last_score())
		self.assertEqual(5,
						report.class_progress[1].get_last_score())

		s = [2,'2018-09-17',result,'all is well', 'no issues', 'try harder next week', '100', 'true', datetime.date(2019,5,30)]
		sql.sql.insert_results(s)

		report = utils.weekly_report.create_weekly_report('2018-09-03', '2018-09-17')
		self.assertEqual(2, len(report.results))

		report = utils.weekly_report.create_weekly_report('2018-09-03', '2018-09-17', student=2)
		self.assertEqual(1, len(report.results))

		# End date outside of the course. We need to be able to handle that
		# but today we can not. I will need to work on this when I have a few minutes
		#TODO 
		# report = utils.weekly_report.create_weekly_report('2018-09-03', '2019-01-07')
		# self.assertEqual(2, len(report.results))



	def test_weekly_report_with_missing(self):
		print('--------------------Start--------------------')
		sql.sqlutil.init_users()
		self.assertEqual(0, sql.sqlutil.init_results())

		result = '{"SQL":1,"JS Logic":2}'
		s = [1,'2018-09-03',result,'all is well', 'no issues', 'try harder next week', '100', 'true', datetime.date(2019,5,30)]
		sql.sql.insert_results(s)
		result = '{"SQL":1,"JS Logic":3}'
		s = [1,'2018-09-10',result,'all is well', 'no issues', 'try harder next week', '100', 'true', datetime.date(2019,5,30)]
		# sql.sql.insert_results(s)
		result = '{"SQL":1,"JS Logic":4}'
		s = [1,'2018-09-17',result,'all is well', 'no issues', 'try harder next week', '100', 'true', datetime.date(2019,5,30)]
		sql.sql.insert_results(s)

		report = utils.weekly_report.create_weekly_report('2018-09-03', '2018-09-17')

		print(report.class_progress[1].get_weekly_results())
		print(report.class_progress[1].weekly)
		print(report.results)
		# self.assertEqual([3,4,5], report.class_progress[1].weekly)
