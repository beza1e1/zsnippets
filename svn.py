"""
Alternative svn library for some easy utility functions
"""
import os
from shell import execute
from datetime import datetime
os.environ['LANG'] = "C" # unify output to english

_INFO_KEYS = {
	"Path: ": 'path',
	"URL: ": 'url',
	"Repository Root: ": 'root_url',
	"Repository UUID: ": 'uuid',
	"Revision: ": 'revision',
	"Last Changed Author: ": 'last_author',
	"Last Changed Rev: ": 'last_revision',
	"Last Changed Date: ": 'last_date',
}
def _get_info(svn_url):
	info = dict()
	for line in execute("svn info "+svn_url):
		for start, key in _INFO_KEYS.items():
			if line.startswith(start):
				info[key] = line[len(start):]
	return info

def _read_status_line(line):
	r,a,d,l = line.split("|")
	r = int(r[1:])
	a = a.strip()
	d = datetime.strptime(d.strip()[:19], "%Y-%m-%d %H:%M:%S") # TODO timezone offset
	l = int(l.strip().split(" ")[0])
	return r,a,d,l

def _get_commit(svn_url, revision):
	diff = "\n".join(execute("svn diff -c%d %s" % (revision, svn_url)))
	lines = execute("svn log -c%d %s" % (revision, svn_url))
	while not lines.next().startswith("---"):
		pass
	status_line = lines.next()
	assert status_line.startswith("r")
	r,a,d,l = _read_status_line(status_line)
	commit = dict(diff=diff, revision=r, author=a, date=d, lines=l)
	msg = list()
	line = lines.next() # skip empty line
	line = lines.next()
	while not line.startswith("---"):
		msg.append(line)
		line = lines.next()
	commit['message'] = "\n".join(msg)
	return commit

def _get_logs(svn_url):
	BLOCK_SIZE = 30
	r = 0
	for line in execute("svn log -l %d %s" % (BLOCK_SIZE, svn_url)):
		if line.startswith("r"):
			try:
				radl = _read_status_line(line)
				r = radl[0]
				yield radl
			except ValueError:
				pass
	while r:
		for line in execute("svn log -r%d:%d %s" % (r-BLOCK_SIZE, r, svn_url)):
			if line.startswith("r"):
				try:
					radl = _read_status_line(line)
					r = radl[0]
					yield radl
				except ValueError:
					pass 
	
def htmlize_diff(diff):
	lines = []
	for line in diff.split("\n"):
		if line.startswith("+++") or line.startswith("---") or line.startswith("===") or line.startswith("Index"):
			line = '<span class="meta">%s</span>' % line
		elif line.startswith("+"):
			line = '<span class="add">%s</span>' % line
		elif line.startswith("-"):
			line = '<span class="remove">%s</span>' % line
		elif line.startswith("@@"):
			line = '<span class="jump">%s</span>' % line
		lines.append(line)
	return "\n".join(lines)

class SVNRepo:
	def __init__(self, url):
		self.url = _get_info(url)['root_url']
		self.update()
		self._commit_cache = dict()
	def update(self):
		"""Update repository information"""
		self.info = _get_info(self.url)
	def _get_max_revision(self):
		return int(self.info['revision'])
	max_revision = property(_get_max_revision)
	def get_commit(self, revision):
		"""Get info about a specific commit"""
		if revision in self._commit_cache:
			return self._commit_cache[revision]
		else:
			c = _get_commit(self.url, revision)
			self._commit_cache[revision] = c
			return c
	def get_revisions_since(self, datetime):
		for r,a,d,l in _get_logs(self.url):
			if d > datetime:
				yield r
			else:
				break

if __name__ == "__main__":
	R = SVNRepo("svn+ssh://zwinkau@ssh.info.uni-karlsruhe.de/ben/firm/svn")
	R.get_commit(R.max_revision)
	print R.get_revisions_since(datetime(2010,3,20))

