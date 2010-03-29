"""
Convenience function
Alternative to subprocess and os.system
"""
import subprocess

def execute(cmd, stderr=True, stdout=True):
	"""Execute a shell command and return stderr and/or stdout data"""
	out, err = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
	try:
		if stderr:
			for line in err.split('\n'):
				yield line
		if stdout:
			for line in out.split('\n'):
				yield line
	except Exception as e:
		print "'%s' -> %s" % (c, e)
	
if __name__ == "__main__":
	for line in execute("hostname"):
		print line
	for line in execute("hostname", True, True):
		print line
	
