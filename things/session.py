
class Session(object):
	def __init__(self, id, email, date):
		self.id = id
		self.email = email
		self.date = date

	def __str__(self):
		return f'User=id: {self.id}, email: {self.email}, date: {self.date}'

	def __repr__(self):
		return self.__str__()
