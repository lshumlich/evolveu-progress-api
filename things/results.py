
import datetime

import json
import things.struc


class Result(things.struc.Struc):
	def __init__(self, date, student_id, student, results, going_well, issues, what_to_try, exercise, industryproj, predcompdate):
		self.date = date
		self.student_id = student_id
		self.student = student
		self.set_results(results)
		self.going_well = going_well
		self.issues = issues
		self.what_to_try = what_to_try
		self.exercise = exercise
		self.industryproj = industryproj
		self.predcompdate = predcompdate
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

	def field_name(self):
		return f'{self.first_name()}_{self.student_id}'

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

	def total_for_questions(self, questions):
		sum = 0
		for q in questions:
			value = self.results_val.get(q['code'],0)
			sum += value
		return sum

	def get_prev_total_for_questions(self, level, questions):
		result = self.get_prev_result(level)
		if result:
			return result.total_for_questions(questions)
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
		return f'Result=student: {self.student_id} {self.student}, date: {self.date}, result: {self.results_val}, going_well: {self.going_well}, issues: {self.issues}, what_to_try: {self.what_to_try}'

	def __repr__(self):
		return self.__str__()

	def reprJSON(self):
		# print(self.__dict__)
		return self.__dict__
		# return json.dumps(self.__dict__)
		# return json.dumps(self, default=lambda o: o.__dict__)
		# return json.dumps(self, default=lambda o: o.__dict__, 
  #           sort_keys=True, indent=4)


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        elif isinstance(obj, datetime.date):
        	return obj.__str__()
        else:
            return json.JSONEncoder.default(self, obj)