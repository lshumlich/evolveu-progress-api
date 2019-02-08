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

		result = '{"sql":1,"logic":2}'
		s = [1,'2018-09-03',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)
		result = '{"sql":1,"logic":3}'
		s = [1,'2018-09-10',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)
		result = '{"sql":1,"logic":4}'
		s = [1,'2018-09-17',result,'all is well', 'no issues', 'try harder next week']
		sql.sql.insert_results(s)

		report = utils.weekly_report.create_weekly_report('2018-09-03', '2018-09-17')
		self.assertEqual(2, report.week_number)
		self.assertEqual(1, len(report.results))
		self.assertEqual(1, len(report.missing))

		self.assertEqual('Target',report.class_progress[0].name)
		self.assertEqual([0,7,14], report.class_progress[0].weekly)

		self.assertEqual('Larry Shumlich',report.class_progress[1].name)
		self.assertEqual([3,4,5], report.class_progress[1].weekly)

		self.assertEqual([{'week':0, 'score':0},{'week':1, 'score':7},{'week':2, 'score':14}],
						report.class_progress[0].get_weekly_results())
		self.assertEqual([{'week':0, 'score':3},{'week':1, 'score':4},{'week':2, 'score':5}],
						report.class_progress[1].get_weekly_results())

		self.assertEqual(14,
						report.class_progress[0].get_last_score())
		self.assertEqual(5,
						report.class_progress[1].get_last_score())

		s = [2,'2018-09-17',result,'all is well', 'no issues', 'try harder next week']
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
