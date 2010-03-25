"""
Uniform access means that o.foo is equal to o.foo().
This can not be mad really equal in Python, but we can allow o.foo, by disallowing o.foo().
"""

class ua_object(object):
	def __setattr__(self, key, value):
		if callable(value) and value.func_code.co_argcount == 1:
			bmethod = value.__get__(self, type(self))
			self.__dict__["__ua_"+key] = bmethod
		else:
			self.__dict__[key] = value
	def __getattr__(self, key):
		return self.__dict__["__ua_"+key]()
	def __delattr__(self, key):
		try:
			del self.__dict__["__ua_"+key]
		except KeyError:
			del self.__dict__[key]

if __name__ == "__main__":
	o = ua_object()
	o.bar = 5
	o.foo = lambda self: self.bar + 2
	assert o.foo == 7
	del o.foo
	del o.bar
