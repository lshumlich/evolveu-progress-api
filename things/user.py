
class User(object):
	def __init__(self, id, name, email, uuid, start_date, admin):
		self.id = id
		self.name = name
		self.email = email
		self.uuid = uuid
		self.start_date = start_date
		self.admin = admin

	def __str__(self):
		return f'User=id: {self.id}, name: {self.name}, email: {self.email}, uuid: {self.uuid}, start_date: {self.start_date}, admin: {self.admin}'

	def __repr__(self):
		return self.__str__()
