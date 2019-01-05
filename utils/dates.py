import datetime
from things.struc import Struc 

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
	try:
		return datetime.datetime.strptime(dt, "%Y-%m-%d").date()
	except:
		return datetime.datetime.now().date()

def course_weeks(s, count):
	if type(s) == str:
		s = to_date(s)

	result = {}
	result[str(s)] = 0

	for i in range (1, count + 1):
		s = next_monday(s)
		result[str(s)] = i
	return result
#
#	start_monday	- The day the course started
#	display_date	- The date the user has asked to be displayed
#	this_monday		- The current Monday
#	prev_monday		- The previous Monday that could be displayed. It can 
#					  not be before the start_Monday
#	display_monday	- The monday that we should be displaying
#	next_monday		- The next Monday that could be displayed. It can not be
#					  past this_Monday
#
def scroll_mondays(start_monday, display_date=None):

	r = Struc()

	if type(start_monday) == str:
		r.start_monday = to_date(start_monday)
	else:
		r.start_monday = start_monday

	r.this_monday = my_monday(datetime.datetime.now().date())

	if not display_date:
		r.display_monday = r.this_monday
	elif type(display_date) == str:
		r.display_monday = my_monday(to_date(display_date))
	else:
		r.display_monday = my_monday(display_date)
	
	r.next_monday = next_monday(r.display_monday)
	r.prev_monday = last_monday(r.display_monday)

	if r.display_monday <= r.start_monday:
		r.prev_monday = None

	if r.display_monday >= r.this_monday:
		r.next_monday = None

	return r
