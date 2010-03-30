from threading import Thread
"""
Futures are a simple way to execute stuff in parallel.
Synchronization is left to the user, though.
"""

# TODO use a thread pool for faster start up

class _Future(Thread):
	def __init__(self, func):
		Thread.__init__(self)
		assert not hasattr(self, '__func')
		assert not hasattr(self, 'result')
		self.__func = func
	def run(self):
		self.result = self.__func()

def future(func):
	"""Returns a promise of the result of func()"""
	t = _Future(func)
	t.start()
	return t

def force(future):
	"""Gets the result of a promise"""
	if future.is_alive():
		future.join()
	return future.result

if __name__ == "__main__":
	sum = 0
	def add(i):
		global sum
		sum += i
	futures = []
	for i in range(100):
		futures.append( future(lambda: add(i)) )
	for f in futures:
		force(f)
	print sum
	

		
