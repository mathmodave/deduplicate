#!/usr/bin/python

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

import filecmp
import md5File
import os
import signal
import sys

STOP = False

def sigintHandler(x, y):
	global STOP
	STOP = True

def inode(filename):
	return os.stat(filename).st_ino	

def checkDuplicate(curInode, curFilename, curHash):
	for altFilename in hashToFilename[curHash]:
		altInode = inode(altFilename)
		if altInode == curInode:
			return True
		else:
			#print 'Possibly duplicates: %s %s' % (altFilename, curFilename)
			if filecmp.cmp(altFilename, curFilename, False):

				prefix = os.path.commonprefix([altFilename, curFilename])
				prefixLength = len(prefix)
				f1 = altFilename[prefixLength:]
				f2 = curFilename[prefixLength:]

				curStat = os.stat(curFilename)
				altStat = os.stat(altFilename)
				mtime = max(curStat.st_mtime, altStat.st_mtime)
				atime = max(curStat.st_atime, altStat.st_atime)

				print 'Deleting %s' % curFilename
				os.unlink(curFilename)

				print 'Linking %s' % f1
				print '  --->  %s' % f2
				os.link(altFilename, curFilename)
				os.utime(altFilename, (atime, mtime))
				return True
	return False

if __name__ == '__main__':

	inodeToHash = {}
	hashToFilename = {}

	signal.signal(signal.SIGINT, sigintHandler)

	inputFile = sys.argv[1]
	f = open(inputFile, 'r')

	while True:
		curFilename = f.readline().strip()
		if curFilename == '':
			break

		if os.path.isdir(curFilename):
			print 'Skipping Directory: %s' % curFilename
			continue

		curInode = inode(curFilename)

		if curInode not in inodeToHash:
			inodeToHash[curInode] = md5File.md5File(curFilename, 32768)

		curHash = inodeToHash[curInode]

		if curHash in hashToFilename:
			if not checkDuplicate(curInode, curFilename, curHash):
				hashToFilename[curHash].append(curFilename)
		else:
			hashToFilename[curHash] = [curFilename]

		if STOP:
			break
				

