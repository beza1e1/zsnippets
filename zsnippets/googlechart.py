
def googlechart_url(**kwargs):
	url = "http://chart.apis.google.com/chart?"
	args = list()
	type = kwargs.pop('type', 'lc')
	args.append('cht=' + type)
	height = kwargs.pop('height', 200)
	width  = kwargs.pop('width', 400)
	args.append('chs=%dx%d' % (width, height))
	data = kwargs.pop('data', [[1,2,3,4,3], [2,4,3,1,2]])
	maxd = 0
	mind = 0
	for line in data:
		for d in line:
			maxd = max(maxd, d)
			mind = min(mind, d)
	args.append('chds=%d,%d' % (mind, maxd))
	def _data_line(lst):
		return ",".join(map(str, lst))
	data = "|".join(map(_data_line, data))
	args.append('chd=t:' + data)
	legend = kwargs.pop('legend', ['red', 'blue'])
	args.append('chdl=' + "|".join(legend))
	colors = kwargs.pop('colors', "FF0000 00FF00 0000CC FF00FF 00FFFF 8888FF 880000 008800 000088 888888 339999 3399FF 9933CC FF6633 996600 880088".split(" "))
	args.append('chco=' + ",".join(colors))

	for k,v in kwargs.items():
		args.append('%s=%s' % (k, v))
	args = "&".join(args)
	return url + args

