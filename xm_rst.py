#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# PYTHON_ARGCOMPLETE_OK
# ExMakhina reStructuredText timesheets stuff

import sys, argparse, re, datetime, decimal, logging

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

	parser_log.add_argument("--when",
	 type=datetimeparse.parse_date,
	 help="date to consider",
	)

	parser_log.add_argument("--name",
	 help="name to consider",
	)

	parser_timesheet = subparsers.add_parser(
	 'timesheet',
	 help="manage timesheet stuff (eg. counting hours)",
	)

	parser_timesheet.add_argument("--rate",
	 type=decimal.Decimal,
	 help="hourly rate",
	)

	parser_timesheet.add_argument("--range",
	 type=ts_range,
	 action="append",
	 required=True,
	 help="[a,b[ range to consider (can be repeated)",
	)

	parser_timesheet.add_argument("--match",
	 help="Only match entries matching this regexp",
	)

	parser_timesheet.add_argument("filename",
	 help="log file to process",
	)

	parser_ts = subparsers.add_parser(
	 'ts',
	 help="shortcut for 'log ts' to produce a timestamp",
	)


	parser_cb = subparsers.add_parser(
	 'clipboard',
	 help="manage clipboard",
	)

	parser_cb_sp = parser_cb.add_subparsers(
	 help='the clipboard command; type "%s clipboard COMMAND -h" for command-specific help' % sys.argv[0],
	 dest='cb_command',
	)

	parser_cb_quote = parser_cb_sp.add_parser(
	 'quote',
	 help="prefix clipboard lines with \"> \"",
	)

	parser_cb_stats = parser_cb_sp.add_parser(
	 'stats',
	 help="statistics on clipboard contents",
	)


	try:
		import argcomplete
		argcomplete.autocomplete(parser)
	except:
		pass

	args = parser.parse_args()

	if args.command == 'log':
		f = getattr(xm_rst_log, "log_" + args.logcommand)
		type_xform = {
		 "when": lambda x: x,
		 "name": str,
		}
		d = dict()
		for k, xform in type_xform.items():
			v = getattr(args, k)
			if v is not None:
				d[k] = xform(v)
		s = f(**d)
		xm_rst_log.log_echo(s)

	elif args.command == "timesheet":
		import xm_rst_to_timesheet_estimation
		total_times = list()
		total_matxs = list()
		for date_range in args.range:
			if args.match:
				def match(x):
					return re.match(args.match, x) is not None
			else:
				match = lambda x: True

			times, matxs = xm_rst_to_timesheet_estimation.process(args.filename, date_range, match)
			total_times += times
			total_matxs += matxs
		total_time = datetime.timedelta()
		print("Time Entries:")
		for date, date_work, comment in total_times:
			print("- %s: %s %s" % (date.strftime("%Y-%m-%d"), datetimeparse.timedelta_str(date_work), comment))
			total_time += date_work
		total_matx = decimal.Decimal(0)
		print("Materials Entries:")
		for date, date_mats in total_matxs:
			print("- %s: %s" % (date.strftime("%Y-%m-%d"), date_mats))
			total_matx += date_mats
		hours = total_time.total_seconds() / (60.0*60)
		note = ""
		if args.rate:
			note = " (%s)" % (decimal.Decimal(hours) * args.rate)
		print("Time Total %.2f h%s" % (hours, note))
		print("Materials Total %s" % (total_matx))

	elif args.command == "ts":
		xm_rst_log.log_echo(xm_rst_log.log_ts())
	elif args.command == "clipboard":
		if args.cb_command == "stats":
			import subprocess
			cmd = "xclip -selection primary -out".split()
			lines = subprocess.check_output(cmd).decode().splitlines()
			lines = [x for x in lines if x != ""]
			words = 0
			for line in lines:
				words += len(line.split())
			print("Lines: %d" % len(lines))
			print("Words: %d" % words)
		elif args.cb_command == "quote":
			import subprocess
			cmd = "xclip -selection primary -out".split()
			out = subprocess.check_output(cmd)
			txt = b"> " + out.replace(b"\n", b"\n> ")
			cmd = "xclip -selection clipboard".split()
			proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
			proc.stdin.write(txt)
			proc.stdin.close()
			res = proc.wait()
			assert res == 0
			print(txt)
		else:
			raise NotImplementedError(args)
	else:
		raise NotImplementedError(args)

