import threading
"""
Futures are a simple way to execute stuff in parallel.
Synchronization is left to the user, though.
"""

class Promise:
	def __init__(self, func):
		self.func = func
		self.lock = threading.Lock()
		self.done = False
	def force(self):
		self.lock.acquire()
		if not self.done:
			self.result = self.func()
			self.done = True
		self.lock.release()
		return self.result

_PROMISES = list()

def _do_promise():
	while len(_PROMISES) > 0:
		p = _PROMISES.pop(0) # empty list exception in concurrent case?
		p.force()

def add_worker(n=1):
	"""Add a worker thread to fulfill promises"""
	t = None
	for i in xrange(n):
		t = threading.Thread(target=_do_promise)
		t.setDaemon(True)
		t.start()
	return t
	
_BASE_WORKER = None
def future(func, *args, **kwargs):
	"""Returns a promise of the result of func()"""
	global _BASE_WORKER
	p = Promise(lambda: func(*args, **kwargs))
	_PROMISES.append(p)
	if not _BASE_WORKER or not _BASE_WORKER.isAlive():
		_BASE_WORKER = add_worker()
	#print len(_PROMISES), _BASE_WORKER
	return p

if __name__ == "__main__":
	import sys
	extra_threads = 0
	if len(sys.argv) > 1:
		extra_threads = int(sys.argv[1])
	S = 0
	end = 1000
	def add(i):
		global S
		S += i
		sum(range(100000))
	promises = []
	for i in range(end):
		promises.append( future(add, i) )
	add_worker(extra_threads)
	print "started %d extra worker threads" % extra_threads
	for p in promises:
		p.force()
	print S, sum(range(end))
	

		
