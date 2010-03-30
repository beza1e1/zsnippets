"""
Convenience function
Alternative to subprocess and os.system
"""
import subprocess
import sys

def execute(cmd, env=None):
	"""Execute a command and return stderr and/or stdout data"""
	out, err = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,\
							env=env).communicate()
	try:
		for line in out.splitlines():
			yield line
	except Exception, e:
		print "'%s' -> %s" % (c, e)
	
def silent_shell(cmd, env=None, debug=False):
	"""Execute a shell command"""
	if debug:
		print "silent_shell", cmd
		stdout = None
		stderr = None
	else:
		stdout = open("/dev/null", 'a')
		stderr = subprocess.STDOUT
	try:
	    return subprocess.call(cmd, shell=True, stdout=stdout, stderr=stderr, env=env)
	except OSError, e:
	    print >>sys.stderr, "Execution failed:", e
	
def write_file(filename, content):
	fh = open(filename, 'w')
	fh.write(content)
	fh.close()

if __name__ == "__main__":
	for line in execute("hostname"):
		print line
	for line in execute("hostname", True, True):
		print line
	
