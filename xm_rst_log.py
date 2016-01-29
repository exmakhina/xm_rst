#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Log writing utilities

import sys, os, io, subprocess, time, datetime, uuid

def printf(x):
	sys.stdout.write(x)
	sys.stdout.flush()


def log_echo(txt):
	cmd = "xclip -selection clipboard".split()
	proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
	proc.stdin.write(txt)
	proc.stdin.close()
	res = proc.wait()
	assert res == 0
	print(txt)

def log_uuid():
	guid = uuid.uuid1(node=0x092120172)
	s = "%s" % guid
	return s

def log_admonition(a):
	s = ".. admonition:: %s\n\n   " % a
	return s

def log_requirement():
	x = log_uuid()
	return log_admonition("Requirement :reqid:\`%s\`" % x)

def log_heading(decorator, title):
	underline = len(title) * decorator
	return "\n%s\n%s\n\n" % (title, underline)

def log_date_header(d=None):
	d = d or datetime.datetime.now()
	return log_heading("=", d.strftime("%Y-%m-%d (%a)"))

def log_timestamp(d=None):
	d = d or datetime.datetime.now()
	return d.strftime("%Y-%m-%dT%H:%M:%S")

def log_ts(d=None):
	d = d or datetime.datetime.now()
	return ":time:`%s`" % d.strftime("%H:%M:%S")

def log_day():
	return "".join([
	 log_date_header(),
	 "\n\n",
	 log_admonition("TODO"),
	 "- TODO\n\n",
	 log_admonition("Done"),
	 "- TODO\n\n"
	])

def log_day_consulting(name=None):
	if name is None:
		import getpass
		name = getpass.getuser()

	return "".join([
	 "\n\n",
	 ".. raw:: latex\n",
	 "\n",
	 "   \\newpage\n",
	 log_date_header(),
	 "\n",
	 log_admonition("TODO"),
	 "- TODO\n\n",
	 log_admonition("Hours - %s" % name),
	 "- TODO\n\n",
	 log_admonition("Done"),
	 "- TODO\n\n",
	 ":Worked: - %s: TODO\n\n" % name,
	 log_heading("+", "The Plan"),
	 "TODO\n\n",
	 log_heading("+", "WIP Notes"),
	 "TODO\n\n",
	 ])

