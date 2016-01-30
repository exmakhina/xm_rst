#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# PYTHON_ARGCOMPLETE_OK
# ExMakhina reStructuredText timesheets stuff

import sys, argparse, re, datetime

import datetimeparse

def printf(x):
	sys.stdout.write(x)
	sys.stdout.flush()

def ts_range(x):
	if x is None:
		t_a = datetime.datetime.now() - datetime.timedelta(days=7)
		t_b = datetime.datetime.now()
	else:
		m = re.match("(?P<ta>.*) to (?P<tb>.*)", x)
		assert m is not None
		tsa = m.group("ta")
		tsb = m.group("tb")

		t_a = datetimeparse.parse_date(tsa)
		t_b = datetimeparse.parse_date(tsb)

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
		print("Entries:")
		for date, date_work in entries:
			print("- %s: %s" % (date.strftime("%Y-%m-%d"), datetimeparse.timedelta_str(date_work)))
			total += date_work
		print("Total %.2f h" % (total.total_seconds() / (60.0*60)))
	elif args.command == "ts":
		xm_rst_log.log_echo(xm_rst_log.log_ts())
	else:
		raise NotImplementedError(args)


