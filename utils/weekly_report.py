
import datetime
import utils.dates
import sql.sql
import sql.sqlutil
import things.struc

class WeeklyReport (things.struc.Struc):
	None

class Progress (things.struc.Struc):
	def __init__(self):
		self.weekly = []

	def get_weekly_results(self):
		results = []
		for i, score in enumerate(self.weekly, start=0):
			results.append({"week": + i , "score" : score})
		return results

	def get_last_score(self):
		if self.weekly:
			return self.weekly[-1]
		return 0


# week_number = 0
# results = {}
# questions = []
# missing = []
# class_progress = []

def create_weekly_report(start_date, report_date, student=None):

	# global week_number, results, questions, missing, progress

	wr = WeeklyReport()

	course_length_weeks = 15

	course_mondays = utils.dates.course_weeks(start_date, course_length_weeks)
	if not report_date:
		report_date = str(utils.dates.my_monday(datetime.datetime.now().date()))

	wr.report_date = report_date
	wr.student = student

	wr.week_number = course_mondays.get(report_date, course_length_weeks)

	wr.results = sql.sql.get_prev_results_obj(level=wr.week_number, date=report_date, order="date, name", student=student)
	wr.questions = sql.sql.get_questions()
	wr.missing = sql.sql.get_missing_for_date(report_date)

	target_points = 5 * len(wr.questions)

	#
	# Get the progress numbers. Start with a 'Target'
	#

	wr.class_progress = []
	progress = Progress()
	wr.class_progress.append(progress)
	progress.name = 'Target'
	progress.weekly = []
	for i in range(0, wr.week_number+1):
		progress.weekly.append(int(i / course_length_weeks * target_points))

	for s in wr.results:
		progress = Progress()
		wr.class_progress.append(progress)
		progress.name = s.student
		# progress.weekly = []
		for i in range(wr.week_number, -1, -1):
			progress.weekly.append(s.get_prev_total(i))

	return wr
