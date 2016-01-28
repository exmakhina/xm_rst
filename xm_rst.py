#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# PYTHON_ARGCOMPLETE_OK
# ExMakhina reStructuredText timesheets stuff

import sys, argparse, re, datetime


def printf(x):
	sys.stdout.write(x)
	sys.stdout.flush()

def ts_range(x):
	if x is None:
		t_a = datetime.datetime.now() - datetime.timedelta(days=7)
		t_b = datetime.datetime.now()
	else:
		m = re.match("(?P<ta>\S+) to (?P<tb>\S+)", x)
		assert m is not None
		tsa = m.group("ta")
		tsb = m.group("tb")
		def parse_date(ts):
			t = None
			if t is None and ts == "now":
				t = datetime.datetime.now()
			if t is None and ts == "yesterday":
				t = datetime.datetime.now()-datetime.timedelta(days=1)

			if t is None:
				try:
					t = datetime.datetime.strptime(ts, "%Y-%m-%d")
				except ValueError:
					pass

			if t is None:
				raise NotImplementedError()

			return t

		t_a = parse_date(tsa)
		t_b = parse_date(tsb)

	return t_a, t_b

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
	 description="reStructuredText helper",
	)


	import xm_rst_log
	choices = []
	for x in dir(xm_rst_log):
	   if x.startswith("log_"):
		  choices.append(x[4:])

	subparsers = parser.add_subparsers(
	 help='the command; type "%s COMMAND -h" for command-specific help' % sys.argv[0],
	 dest='command',
	)

	parser_log = subparsers.add_parser(
	 'log',
	 help="manage additions to log files",
	)

	parser_log.add_argument("logcommand",
    choices=choices,
	 help="",
	)

	parser_timesheet = subparsers.add_parser(
	 'timesheet',
	 help="manage timesheet stuff (eg. counting hours)",
	)

	parser_timesheet.add_argument("--range",
	 type=ts_range,
	 action="append",
	 help="[a,b[ range to consider (can be repeated)",
	)

	parser_timesheet.add_argument("filename",
	 help="log file to process",
	)

	parser_ts = subparsers.add_parser(
	 'ts',
	 help="shortcut for 'log ts' to produce a timestamp",
	)

	try:
		import argcomplete
		argcomplete.autocomplete(parser)
	except:
		pass

	args = parser.parse_args()

	import xm_rst_to_timesheet_estimation

	if args.command == 'log':
		xm_rst_log.log_echo(getattr(xm_rst_log, "log_" + args.logcommand)())
	elif args.command == "timesheet":
		entries = []
		for date_range in args.range:
			entries += xm_rst_to_timesheet_estimation.process(args.filename, date_range)
		total = datetime.timedelta()
		for date, date_work in entries:
			total += date_work
		print("Total %.2f h" % (total.total_seconds() / (60.0*60)))
	elif args.command == "ts":
		xm_rst_log.log_echo(xm_rst_log.log_ts())
	else:
		raise NotImplementedError(args)


