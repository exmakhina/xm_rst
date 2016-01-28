#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Gets worked hours from a rst document

import sys, os, re, datetime

import docutils
import docutils.nodes
import docutils.utils
import docutils.parsers.rst
import docutils.frontend

def process(filename, date_range):
	settings = docutils.frontend.OptionParser(
	 components=(docutils.parsers.rst.Parser,)) \
	 .get_default_values()
	document = docutils.utils.new_document(filename, settings)
	parser = docutils.parsers.rst.Parser()
	with open(filename, "rb") as f:
		input = f.read().decode('utf-8')
	parser.parse(input, document)
	class V():
		def __init__(self, document, date_range):
			self.document = document
			self.entries = []
			self.date = None
			self.date_range = date_range
			self.min_date = date_range[0]
			self.max_date = date_range[1]

		def visit(self, node):
			#print(node)
			pass
		def dispatch_visit(self, node):
			#print(node)
			if node.__class__ == docutils.nodes.section:
				title = node.children[0].rawsource
				m = re.match(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2}) \((Mon|Tue|Wed|Thu|Fri|Sat|Sun)\)", title)
				if m is None:
					#print("Skipping %s" % title)
					return
				def toi(x): return int(m.group(x))
				self.date = datetime.datetime(year=toi("y"), month=toi("m"), day=toi("d"))
				self.date = self.date.replace(second=1)

			if node.__class__ == docutils.nodes.admonition:
				title = node.children[0].rawsource
				if not title.startswith("Hours"):
					return

				assert self.date is not None, "Sonna bakana!"
				print("- %s" % self.date.strftime("%Y-%m-%d"))

				assert node.children[1].__class__ == docutils.nodes.bullet_list, node.children[1]
				entries = node.children[1].children

				dayjob = datetime.timedelta()

				print("  - Entries:")
				for entry in entries:
					assert len(entry.children) == 1, entry
					assert entry.children[0].__class__ == docutils.nodes.paragraph
					pr = entry.children[0].rawsource
					p = pr.splitlines()[0]
					pr = pr.replace("\n", " ")
					re_a = r"^From :time:`(?P<from>\d{2}:\d{2}:\d{2})` to :time:`(?P<to>\d{2}:\d{2}:\d{2})`,?.*$"
					m = re.match(re_a, p)
					if m is not None:
						tsf = m.group("from")
						tst = m.group("to")
						f = datetime.datetime.strptime(tsf, "%H:%M:%S")
						f = f.replace(year=self.date.year, month=self.date.month, day=self.date.day)
						t = datetime.datetime.strptime(tst, "%H:%M:%S")
						t = t.replace(year=self.date.year, month=self.date.month, day=self.date.day)
						if t < f:
							t += datetime.timedelta(hours=24)
						dt = t-f
						dayjob += dt
						print("    - %s: %s" % (dt, pr))

						if f < self.min_date:
							f = self.min_date
						if t > self.max_date:
							t = self.max_date
						if t > f:
							print("     Considered %s" % (t-f))
							self.entries.append((self.date, t-f))
						continue

					re_a = r"^From :time:`(?P<from>\d{2}:\d{2})` to :time:`(?P<to>\d{2}:\d{2})`,?.*$"
					m = re.match(re_a, p)
					if m is not None:
						tsf = m.group("from")
						tst = m.group("to")
						f = datetime.datetime.strptime(tsf, "%H:%M")
						f = f.replace(year=self.date.year, month=self.date.month, day=self.date.day)
						t = datetime.datetime.strptime(tst, "%H:%M")
						t = t.replace(year=self.date.year, month=self.date.month, day=self.date.day)
						if t < f:
							t += datetime.timedelta(hours=24)
						dt = t-f
						dayjob += dt
						print("    - %s: %s" % (dt, pr))

						if f < self.min_date:
							f = self.min_date
						if t > self.max_date:
							t = self.max_date
						if t > f:
							print("     Considered %s" % (t-f))
							self.entries.append((self.date, t-f))
						continue

					re_a = r"^Estimated :time:`((?P<h>\d+)h)?((?P<m>\d+)m?)?`,?\s*.*$"
					m = re.match(re_a, p)
					if m is not None:
						d = dict(m.groupdict())
						h = int(d.get('h', 0) or 0)
						m = float(d.get("m", 0) or 0)
						dt = datetime.timedelta(hours=h, minutes=m)
						print("    - %s: %s" % (dt, pr))
						dayjob += dt
						if self.date >= self.min_date and self.date <= self.max_date:
							self.entries.append((self.date, dt))
						continue

					assert False, p

				#print(dayjob)				
				ts = dayjob.total_seconds()
				h = ts//3600
				m = ts//60 - h*60
				print("  - Day total: %2d:%02d" % (h, m))

		def depart(self, node):
			print(node)

	visitor = V(document, date_range)
	document.walk(visitor)

	return visitor.entries
	
