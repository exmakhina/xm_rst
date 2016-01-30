#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Parse and pretty-print functions for datetime or timedelta

__author__ = "Jérôme Carretero <cJ@zougloub.eu>"
__license__ = "MIT"

import re, datetime

def timedelta_str(x, precision="m"):
	"""
	:return: string corresponding to a time delta
	:param x: timedelta, native or in seconds (float)
	"""
	if isinstance(x, datetime.timedelta):
		ts = x.total_seconds()
	elif isinstance(x, float):
		ts = int(round(x))
	else:
		raise NotImplementedError()

	h = ts//3600
	m = ts//60 - h*60
	return "%2d:%02d" % (h, m)

def inonull(i):
	"""
	:return: a dict containing integer values, only if they existed
	"""
	return dict((key, int(value)) for (key, value) in i.items() if value is not None)

def parse_date(spec):
	"""
	Return a timestamp from some kind of date/time spec
	
	Something more than datetime.datetime.strptime(ts, "%Y-%m-%d")
	"""
	spec = spec.lower()
	try:
		sp = tuple(spec.split())

		out = datetime.datetime.now()

		if spec != 'now':
			
			while True:
				m = re.search(r'(?P<year>\d{4})?-?(?P<month>\d{2})-(?P<day>\d{2})', spec)
				if m is not None:
					g = inonull(m.groupdict())
					out = out.replace(**g)
					break
				
				found = False
				for i in range(1, 8):
					day = out - datetime.timedelta(days=i)
					sh = day.strftime('%a').lower()
					lo = day.strftime('%A').lower()
					if sh in sp or lo in sp:
						out = day
						found = True
						break
				if found:
					break

				if 'yesterday' in spec:
					out -= datetime.timedelta(days=1)
					break
				
				if 'today' in spec or 'this' in spec or 1:
					break
		
			while True:
				m = re.search(r'(?P<hour>\d{2}):(?P<minute>\d{2}):?(?P<second>\d{2})?', spec)
				if m is not None:
					g = inonull(m.groupdict())
					out = out.replace(**g)
					break

				if 'afternoon' in spec:
					out = out.replace(hour=13, minute=00, second=0)
					break

				if 'morning' in spec or 1:
					out = out.replace(hour=9, minute=30, second=0)
					break

		return out

	except Exception as e:
		raise ValueError("Spec not understood: %s (%s)" % (spec, e))

