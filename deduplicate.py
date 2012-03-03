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
	"""Set STOP to True and Stop the main loop"""
	global STOP
	STOP = True

def inode(filename):
	"""Helper function to return inode number of filename"""
	return os.stat(filename).st_ino	

def checkDuplicate(curInode, curFilename, curHash):
	"""Check to see whether curFilename is a duplicate of
	some other file that we've already seen."""

	# hashToFilename[curHash] is a list of all the files
	# that have the same first 32k (up to hash collision)
	# as curFilename	

	for altFilename in hashToFilename[curHash]:
		altInode = inode(altFilename)
		if altInode == curInode:
			return True
		else:
			# curFilename and altFilename have the same first 32k, so 
			# see if they're actually the same file	
			if filecmp.cmp(altFilename, curFilename, False):
				# altFilename and curFilename are identical, so
				# delete curFilename and hardlink it to altFilename

				# The two files may have different properties,
				# in particular atime/mtime; so choose the latest.
				# (perms could also differ, but ignored for now)
				curStat = os.stat(curFilename)
				altStat = os.stat(altFilename)
				mtime = max(curStat.st_mtime, altStat.st_mtime)
				atime = max(curStat.st_atime, altStat.st_atime)

				print 'Deleting %s' % curFilename
				os.unlink(curFilename)

				print 'Linking %s' % altFilename
				print '  --->  %s' % curFilename
				os.link(altFilename, curFilename)
				os.utime(altFilename, (atime, mtime))
				return True
	return False

if __name__ == '__main__':

	inodeToHash = {}
	hashToFilename = {}

	signal.signal(signal.SIGINT, sigintHandler)

	# The input file is simply a list of filenames, one filename per line
	inputFile = sys.argv[1]
	f = open(inputFile, 'r')

	while True:
		curFilename = f.readline().strip()
		if curFilename == '': # EOF
			break

		if os.path.isdir(curFilename): # Ignore directories
			print 'Skipping Directory: %s' % curFilename
			continue

		# Determine the inode number of the current file
		curInode = inode(curFilename)

		if curInode not in inodeToHash:
			# Not seen this inode before, hash the first 32k of the file
			inodeToHash[curInode] = md5File.md5File(curFilename, 32768)

		# Determine the hash of the current file
		curHash = inodeToHash[curInode]

		# Have we seen a file with the same first 32k?
		if curHash not in hashToFilename:
			# No - can't possibly be a duplicate
			hashToFilename[curHash] = [curFilename]
		else:
			# Yes - see whether we have a duplicate
			if not checkDuplicate(curInode, curFilename, curHash):
				# Wasn't a duplicate so add the filename to the list
				hashToFilename[curHash].append(curFilename)

		if STOP:
			# Set by SIGINT
			break
				

