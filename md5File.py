#
# $Id: md5File.py 122 2009-04-10 14:19:16Z dgeo2 $
#

import md5

def md5File(filename, count=None):
	m = md5.new()
	f = open(filename, 'rb')
	while True:
		t = f.read(1024)
		count -= len(t)
		if (len(t) == 0):
			break
		if (count is not None and count <= 0):
			break
		m.update(t)
	f.close()
	return m.hexdigest()
