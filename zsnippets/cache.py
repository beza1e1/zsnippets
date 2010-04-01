import time


class Cache:
	def __init__(self, seconds=1.0):
		self.seconds = seconds
		self._cache = dict()
	def put(self, key, value):
		self._cache[key] = (time.time(), value)
	def get(self, key, default=None):
		t,v = self._cache[key]
		if time.time() - t > self.seconds:
			del self._cache[key]
			if default:
				return default
			else:
				raise KeyError("Value out of date")
		return v
	def __setitem__(self, key, value):
		return self.put(key, value)
	def __getitem__(self, key):
		return self.get(key)
	def __contains__(self, key):
		try: 
			t,v = self._cache[key]
			if time.time() - t > self.seconds:
				del self._cache[key]
				return False
		except KeyError:
			return False
		return True
	def clear(self):
		"""Remove all entries"""
		self._cache.clear()
	
if __name__ == "__main__":
	c = Cache(0.2)
	c.put("foo", 42)
	assert "foo" in c
	assert c.get('foo') == 42
	c.clear()
	assert not "foo" in c
	c.put("bar", 11)
	time.sleep(0.3)
	assert not "bar" in c

