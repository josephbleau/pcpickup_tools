#!/usr/bin/python

# remove_duplicates.py
# A simple script that accepts a file and writes reads it line by line
# removes any duplicate lines, and prints out to a new file with the
# lines printed in alphabetical order.
#
# Author: PC Pickup - www.pcpickup.com

import sys

if __name__ == "__main__":
	if( len(sys.argv) == 2 ):
		filename = sys.argv[1]
		lines = {}		
		
		# Read all lines into a dictionary
		# automatically culling duplicates
		try:
			fh = open(filename)
			for line in fh:
				lines[line] = ""
			fh.close()		
		except:
			print "Error: could not open file '" + filename + "'"
			exit
		
		# Write out sorted dictionary to file
		#  with _nodup appended
		try:
			fh = open(filename + "_nodups", "w")
			keys = lines.keys()
			keys.sort()
			for k in keys:
				fh.write(k)
			fh.close()
		except:
			print "Error: could not write file '"+filename+"_nodup', check permissions."
			exit
	else:
		print "Usage: remove_duplicates.py [filename]"
