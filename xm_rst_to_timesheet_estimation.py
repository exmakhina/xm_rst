#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Gets worked hours from a rst document

import sys, os, re, datetime, decimal, logging

import docutils
import docutils.nodes
import docutils.utils
import docutils.parsers.rst
import docutils.frontend

import datetimeparse


logger = logging.getLogger(__name__)


def process(filename, date_range, match_title=lambda x: True, match=lambda x: True):
	settings = docutils.frontend.OptionParser(
	 components=(docutils.parsers.rst.Parser,)) \
	 .get_default_values()
	document = docutils.utils.new_document(filename, settings)
	parser = docutils.parsers.rst.Parser()
	with open(filename, "rb") as f:
		input = f.read().decode('utf-8')
	parser.parse(input, document)

	class V_time(object):
		def __init__(self, document, date_range):
			self.document = document
			self.entries = []
			self.date = None
			self.date_range = date_range
			self.min_date = date_range[0]
			self.max_date = date_range[1]
			logger.debug(self.min_date)
			logger.debug(self.max_date)

		def visit(self, node):
			#logger.debug(node)
			pass

		def dispatch_visit(self, node):
			#logger.debug(node)
			if node.__class__ == docutils.nodes.section:
				title = node.children[0].rawsource
				m = re.match(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2}) \((?P<weekday>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\)", title)
				if m is None:
					#logger.debug("Skipping %s" % title)
					return
				def toi(x): return int(m.group(x))
				self.date = datetime.datetime(year=toi("y"), month=toi("m"), day=toi("d"))
				self.date = self.date.replace(second=1)

				# Validate day
				weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
				weekday = weekdays.index(m.group("weekday"))
				assert weekday == self.date.weekday(), "Wrong date: {}, DoW should be {}".format(title, self.date.weekday())


			if node.__class__ == docutils.nodes.admonition:
				title = node.children[0].rawsource
				if not match_title(title):
					return

				assert self.date is not None, "Sonna bakana!"
				logger.debug("- %s" % self.date.strftime("%Y-%m-%d"))

				assert node.children[1].__class__ == docutils.nodes.bullet_list, node.children[1]
				entries = node.children[1].children

				dayjob = datetime.timedelta()

				logger.debug("  - Entries:")
				for entry in entries:
					if len(entry.children) != 1 \
					 or entry.children[0].__class__ != docutils.nodes.paragraph:
						raise RuntimeError("Entry should be a single paragraph, not {} in {}\n {}".format(entry.children[0].__class__, self.date, entry.children[0].rawsource))

					pr = entry.children[0].rawsource
					p = pr.replace("\n", " ")#.splitlines()[0]
					pr = pr.replace("\n", " ")
					re_a = r"^From :time:`(?P<from>\d{2}:\d{2}:\d{2})` to :time:`(?P<to>\d{2}:\d{2}:\d{2})`,?(?P<comment>.*)$"
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

						if f < self.min_date:
							f = self.min_date
						if t > self.max_date:
							t = self.max_date

						dt = t-f
						logging.debug("    - %s: %s" % (dt, pr))

						if t > f and match(m.group("comment")):
							dayjob += dt
							logger.debug("    - %s: %s" % (dt, pr))
							self.entries.append((self.date, dt, pr))
						continue

					re_a = r"^From :time:`(?P<from>\d{2}:\d{2})` to :time:`(?P<to>\d{2}:\d{2})`( less :time:`((?P<h>\d+(\.\d+)?)h)?((?P<m>\d+)m?)?`)?,?(?P<comment>.*)$"
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

						if f < self.min_date:
							f = self.min_date
						if t > self.max_date:
							t = self.max_date

						dt = t-f
						d = dict(m.groupdict())
						h_ = float(d.get('h', 0) or 0)
						m_ = float(d.get("m", 0) or 0)
						dt -= datetime.timedelta(hours=h_, minutes=m_)

						logging.debug("    - %s: %s" % (dt, pr))

						if t > f and match(m.group("comment")):
							dayjob += dt
							logger.debug("    - %s: %s" % (dt, pr))
							self.entries.append((self.date, dt, pr))
						continue

					re_a = r"^Estimated :time:`((?P<h>\d+(\.\d+)?)h)?((?P<m>\d+)m?)?`,?\s*(?P<comment>.*)$"
					m = re.match(re_a, p)
					if m is not None:
						d = dict(m.groupdict())
						h_ = float(d.get('h', 0) or 0)
						m_ = float(d.get("m", 0) or 0)
						dt = datetime.timedelta(hours=h_, minutes=m_)
						logging.debug("    - %s: %s" % (dt, pr))
						if self.date >= self.min_date and self.date <= self.max_date and match(m.group("comment")):
							dayjob += dt
							logger.debug("    - %s: %s" % (dt, pr))
							self.entries.append((self.date, dt, pr))
						continue

					assert False, p

				logger.debug("  - Day total: %s" % datetimeparse.timedelta_str(dayjob))

		def depart(self, node):
			logger.debug(node)

	class V_materials(object):
		def __init__(self, document, date_range):
			self.document = document
			self.entries = []
			self.date = None
			self.date_range = date_range
			self.min_date = date_range[0]
			self.max_date = date_range[1]
			logger.debug(self.min_date)
			logger.debug(self.max_date)

		def visit(self, node):
			#logger.debug(node)
			pass

		def dispatch_visit(self, node):
			#logger.debug(node)
			if node.__class__ == docutils.nodes.section:
				title = node.children[0].rawsource
				m = re.match(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2}) \((Mon|Tue|Wed|Thu|Fri|Sat|Sun)\)", title)
				if m is None:
					#logger.debug("Skipping %s" % title)
					return
				def toi(x): return int(m.group(x))
				self.date = datetime.datetime(year=toi("y"), month=toi("m"), day=toi("d"))
				self.date = self.date.replace(second=1)

			if node.__class__ == docutils.nodes.admonition:
				title = node.children[0].rawsource
				if not title.startswith("Expenses"):
					return

				assert self.date is not None, "Sonna bakana!"
				logger.debug("- %s" % self.date.strftime("%Y-%m-%d"))

				assert node.children[1].__class__ == docutils.nodes.bullet_list, node.children[1]
				entries = node.children[1].children

				day_exp = 0

				logger.debug("  - Entries:")
				for entry in entries:
					assert len(entry.children) == 1, entry
					assert entry.children[0].__class__ == docutils.nodes.paragraph
					pr = entry.children[0].rawsource
					p = pr.splitlines()[0]
					pr = pr.replace("\n", " ")
					re_a = r"^:materials:`(?P<amount>[\d.]+) ?(?P<currency>\S+)`,?.*$"
					m = re.match(re_a, p)
					if m is not None:
						v = decimal.Decimal(m.group("amount"))
						c = m.group("currency")
						day_exp += v
						logger.debug("    - %s: %s" % (v, pr))
						if self.date >= self.min_date and self.date <= self.max_date:
							self.entries.append((self.date, v, c))
						continue

					assert False, p

				logger.debug("  - Day total: %s" % day_exp)

		def depart(self, node):
			logger.debug(node)

	visitor_time = V_time(document, date_range)
	document.walk(visitor_time)

	visitor_materials = V_materials(document, date_range)
	document.walk(visitor_materials)

	return visitor_time.entries, visitor_materials.entries

