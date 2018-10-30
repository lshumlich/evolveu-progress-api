
import json


class Result(object):
	def __init__(self, date, student_id, student, results, going_well, issues, what_to_try):
		self.date = date
		self.student_id = student_id
		self.student = student
		self.set_results(results)
		self.going_well = going_well
		self.issues = issues
		self.what_to_try = what_to_try
		self.prev_result_val = None

	def set_results(self, results_val):
		if isinstance(results_val, str):
			self.results_val = json.loads(results_val)
		else:
			self.results_val = results_val

	def get_question_results(self, questions):
		""" 
		return the results in the same order as the questions. It should
		be noted that the key is 'axis' and not 'code'. This is because
		for radial graphs (which this is used for) uses axis.
		"""
		results = []
		for q in questions:
			value = self.results_val.get(q['code'],0)
			results.append({'axis':q['code'],'value':value})
		return results

	def first_name(self):
		return self.student.split()[0]

	def total(self):
		sum = 0
		for i in self.results_val:
			sum += self.results_val[i]
		return sum

	def get_prev_total(self, level):
		result = self.get_prev_result(level)
		if result:
			return result.total()
		return 0

	def get_prev_question_results(self, level, questions):
		result = self.get_prev_result(level)
		if result:
			return result.get_question_results(questions)
		return []

	def set_prev_result(self, level, prev_result):
		result = self.get_prev_result(level)
		if result:
			result.prev_result_val = prev_result

	def get_prev_result(self, level):
		result = self
		for i in range(level):
			if result:
				result = result.prev_result_val
		return result

	def __str__(self):
		return f'Result=student: {self.student}, date: {self.date}, result: {self.results_val}, going_well: {self.going_well}, issues: {self.issues}, what_to_try: {self.what_to_try}'

	def __repr__(self):
		return self.__str__()
