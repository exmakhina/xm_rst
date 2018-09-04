#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Log writing utilities

import sys, os, io, subprocess, time, datetime, uuid, hashlib, base64, struct, binascii

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

def log_node():
	h = hashlib.md5()
	try:
		import pwd
		uid = os.getuid()
		name = pwd.getpwuid(uid).pw_gecos
		if sys.hexversion < 0x03000000 and isinstance(name, bytes):
			name = name.decode("utf-8")
	except ImportError:
		name = "unknown"
	h.update(name.encode("utf-8"))
	d = h.digest()
	return d

def log_uuid(node=None):
	if node is None:
		node = log_node()[:6]
		node = sum(ord(c) << (i * 8) for i, c in enumerate(node[::-1]))
	guid = uuid.uuid1(node=node)
	s = "%s" % guid
	return s

def log_nuuid(node=None):
	"""
	Non-universally-unique identifier:

	- Space/time encoding
	- Compact (12 chars)
	- Legible (RFC 4648 Base32 alphabet)
	"""
	if node is None:
		node = log_node()[:3]
	t0 = datetime.datetime(year=2012, month=1, day=1)
	t1 = datetime.datetime.now()
	dt = t1 - t0
	dt = int(round(dt.total_seconds()*10))
	dts = struct.pack(">I", dt)
	#print(binascii.hexlify(dts))
	#print(binascii.hexlify(node))
	s = dts + node
	s = base64.b32encode(s)[:-4]
	return s

def log_admonition(a):
	s = ".. admonition:: %s\n\n   " % a
	return s

def log_requirement():
	x = log_uuid()
	return log_admonition("Requirement :reqid:`%s`" % x)

def log_requirement2():
	x = log_nuuid()
	return log_admonition("Requirement :reqid:`%s`" % x)

def log_req(name="Requirement"):
	x = log_nuuid()
	return "%s [%s]:" % (name, x)

def log_heading(decorator, title):
	underline = len(title) * decorator
	return "\n%s\n%s\n\n" % (title, underline)

def log_date_header(when=None):
	when = when or datetime.datetime.now()
	return log_heading("=", when.strftime("%Y-%m-%d (%a)"))

def log_timestamp(when=None):
	when = when or datetime.datetime.now()
	return when.strftime("%Y-%m-%dT%H:%M:%S")

def log_ts(when=None):
	when = when or datetime.datetime.now()
	return ":time:`%s`" % when.strftime("%H:%M:%S")

def log_day(when=None):
	return "".join([
	 log_date_header(when=when),
	 "\n",
	 log_admonition("TODO"),
	 "- TODO\n\n",
	 log_admonition("Done"),
	 "- TODO\n\n"
	])

def log_day_consulting(when=None, name=None):
	if name is None:
		import getpass
		name = getpass.getuser()

	return "".join([
	 "\n\n",
	 ".. raw:: latex\n",
	 "\n",
	 "   \\newpage\n",
	 log_date_header(when=when),
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

