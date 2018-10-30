"""
To run the tests from the app root directory

PYTHONPATH=. pytest

--- Select only tests that have questions in the test name and don't hide the output
PYTHONPATH=. pytest -k questions -s

"""
import datetime
import unittest
import utils.dates

class TestDates(unittest.TestCase):

	def test_my_monday(self):
		# All these dates should be Sept 3, a special day
		self.assertEqual(utils.dates.my_monday(datetime.date(2018,9,3)), datetime.date(2018,9,3))
		self.assertEqual(utils.dates.my_monday(datetime.date(2018,9,2)), datetime.date(2018,9,3))
		self.assertEqual(utils.dates.my_monday(datetime.date(2018,9,1)), datetime.date(2018,9,3))
		self.assertEqual(utils.dates.my_monday(datetime.date(2018,8,31)), datetime.date(2018,9,3))
		self.assertEqual(utils.dates.my_monday(datetime.date(2018,8,30)), datetime.date(2018,9,3))

		self.assertEqual(utils.dates.my_monday(datetime.date(2018,9,4)), datetime.date(2018,9,3))
		self.assertEqual(utils.dates.my_monday(datetime.date(2018,9,5)), datetime.date(2018,9,3))

		# Now we flip to Sept 10,
		self.assertEqual(utils.dates.my_monday(datetime.date(2018,9,6)), datetime.date(2018,9,10))

		my_monday = utils.dates.my_monday(datetime.datetime.now().date())

	def test_next_monday(self):
		self.assertEqual(utils.dates.next_monday(datetime.date(2018,9,3)), datetime.date(2018,9,10))
		self.assertEqual(utils.dates.next_monday(datetime.date(2018,8,30)), datetime.date(2018,9,10))

		self.assertEqual(utils.dates.next_monday(datetime.date(2018,9,10)), datetime.date(2018,9,17))
		self.assertEqual(utils.dates.next_monday(datetime.date(2018,9,11)), datetime.date(2018,9,17))

	def test_last_monday(self):
		self.assertEqual(utils.dates.last_monday(datetime.date(2018,9,3)), datetime.date(2018,8,27))
		self.assertEqual(utils.dates.last_monday(datetime.date(2018,8,30)), datetime.date(2018,8,27))

		self.assertEqual(utils.dates.last_monday(datetime.date(2018,9,10)), datetime.date(2018,9,3))
		self.assertEqual(utils.dates.last_monday(datetime.date(2018,9,11)), datetime.date(2018,9,3))

	def test_to_date(self):
		s = '2018-09-03'
		self.assertEqual(utils.dates.to_date(s), datetime.date(2018,9,3))

	def test_course_weeks(self):
		s = '2018-09-03'
		self.assertEqual({'2018-09-03':0, '2018-09-10': 1 },utils.dates.course_weeks(s,1))
		self.assertEqual({'2018-09-03':0, '2018-09-10': 1 , '2018-09-17': 2, '2018-09-24': 3, 
						  '2018-10-01': 4, '2018-10-08': 5  },utils.dates.course_weeks(s,5))

