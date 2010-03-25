"""
Alternative svn library for some easy utility functions
"""
import os
import subprocess
from datetime import datetime
os.environ['LANG'] = "C" # unify output to english

def _my_system(cmd):
	"""Execute a shell command and return stderr and stdout data"""
	stdout, stderr = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
	try:
		for line in stderr.split('\n'):
			yield line
		for line in stdout.split('\n'):
			yield line
	except Exception as e:
		print "'%s' -> %s" % (c, e)

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
	for line in _my_system("svn info "+svn_url):
		for start, key in _INFO_KEYS.items():
			if line.startswith(start):
				info[key] = line[len(start):]
	return info

def _get_commit(svn_url, revision):
	diff = "\n".join(_my_system("svn diff -c%d %s" % (revision, svn_url)))
	commit = dict(diff=diff)
	lines = _my_system("svn log -c%d %s" % (revision, svn_url))
	while not lines.next().startswith("---"):
		pass
	status_line = lines.next()
	assert status_line.startswith("r")
	r,a,d,l = status_line.split("|")
	commit['revision'] = int(r[1:])
	commit['author'] = a.strip()
	commit['date'] = datetime.strptime(d.strip()[:19], "%Y-%m-%d %H:%M:%S") # TODO timezone offset
	commit['lines'] = int(l.strip().split(" ")[0])
	msg = list()
	line = lines.next() # skip empty line
	line = lines.next()
	while not line.startswith("---"):
		msg.append(line)
		line = lines.next()
	commit['message'] = "\n".join(msg)
	return commit

class SVNRepo:
	def __init__(self, url):
		self.url = _get_info(url)['root_url']
		self.update()
	def update(self):
		"""Update repository information"""
		self.info = _get_info(self.url)
	def _get_max_revision(self):
		return int(self.info['revision'])
	max_revision = property(_get_max_revision)
	def get_commit(self, revision):
		"""Get info about a specific commit"""
		print _get_commit(self.url, revision)

if __name__ == "__main__":
	R = SVNRepo("svn+ssh://zwinkau@ssh.info.uni-karlsruhe.de/ben/firm/svn")
	print R.get_commit(R.max_revision)

