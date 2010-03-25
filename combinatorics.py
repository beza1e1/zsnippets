def powerset(seq): 
	"""Returns all the subsets of this set. This is a generator.""" 
	if seq: 
		for item in powerset(seq[1:]): 
			yield [seq[0]]+item 
			yield item 
	else: 
		yield seq

def combinations(dic):
	dic = dic.items()
	number = [0] * len(dic)
	def finished(number):
		for i in xrange(len(number)):
			if number[i] < len(dic[i][1]) - 1:
				return False
		return True
	def inc(number):
		for i in xrange(len(number)):
			if number[i] < len(dic[i][1]) - 1:
				number[i] += 1
				return 
			else:
				number[i] = 0
	while True:
		yield dict((dic[i][0], dic[i][1][j]) for (i,j) in enumerate(number))
		if not finished(number):
			inc(number)
		else:
			break

if __name__ == "__main__":
	lis = list(powerset([11, 42, 1337]))
	dic = {
		'day': ('monday', 'tuesday', 'wednesday'),
		'number': lis,
		'name': ('John', 'Max')
	}
	for c in combinations(dic):
		print c

