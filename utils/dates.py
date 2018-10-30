import datetime

def my_monday(dt):
	"""
	Given a date what is the Monday date that can be edited. We can edit only the Monday that falls
	between Wed - Tue.
	"""
	wd = dt.weekday()
	if wd > 2:
		diff = 7 - wd
	else:
		diff = wd * -1
	return dt + datetime.timedelta(days=diff)

def next_monday(dt):
	return my_monday(dt) + datetime.timedelta(7)


def last_monday(dt):
	return my_monday(dt) - datetime.timedelta(7)

def to_date(dt):
	return datetime.datetime.strptime(dt, "%Y-%m-%d").date()

def course_weeks(s, count):
	if type(s) == str:
		s = to_date(s)

	result = {}
	result[str(s)] = 0

	for i in range (1, count + 1):
		s = next_monday(s)
		result[str(s)] = i;
	return result
