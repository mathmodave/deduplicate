
#    Copyright (C) 2012 David Oxley <git@epsilon.org.uk>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import hashlib
import sys

def md5File(filename, count=None):
	"""Calculate the MD5 sum of the first count bytes of filename.

	If count is none, calculate the hash for the whole file

	"""

	m = hashlib.md5()
	f = open(filename, 'rb')

	if count is None:
		# Bug alert! Files larger than maxint
		# won't be md5'd properly
		count = sys.maxint	

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
