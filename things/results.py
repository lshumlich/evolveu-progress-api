
import json


class Result(object):
	def __init__(self, date, student, result, going_well, issues, what_to_try):
		self.date = date
		self.student = student
		self.result(result)
		self.going_well = going_well
		self.issues = issues
		self.what_to_try = what_to_try

	def result(self, result_val):
		if isinstance(result_val, str):
			self.result_val = json.loads(result_val)
		else:
			self.result_val = result_val

	def first_name(self):
		return self.student.split()[0]

	def total(self):
		sum = 0;
		for i in self.result_val:
			sum += self.result_val[i]
		return sum

	def __str__(self):
		return f'Result=student: {self.student}, date: {self.date}, result: {self.result_val}, going_well: {self.going_well}, issues: {self.issues}, what_to_try: {self.what_to_try}'

	def __repr__(self):
		return self.__str__()
