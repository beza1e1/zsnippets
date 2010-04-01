from time import time

def timing(title, func):
	start = time()
	ret = func()
	end = time()
	print "Timing %.2fsec <%s>" % (end-start, title)
	return ret

