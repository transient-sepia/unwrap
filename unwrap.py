#!/usr/bin/python
#
# This script unwraps Oracle wrapped plb packages, does not support 9g
# Original script info - Contact: niels at teusink net / blog.teusink.net
# modified for personal use
#
# License: Public domain
# 
# unwrap-chan
# version 1.1
#
# / no, but i have an idea. /
#

# imports
import re, base64, zlib, sys, argparse, os, fileinput

# simple substitution table
charmap = [0x3d, 0x65, 0x85, 0xb3, 0x18, 0xdb, 0xe2, 0x87, 0xf1, 0x52, 0xab, 0x63, 0x4b, 0xb5, 0xa0, 0x5f, 0x7d, 0x68, 0x7b, 0x9b, 0x24, 0xc2, 0x28, 0x67, 0x8a, 0xde, 0xa4, 0x26, 0x1e, 0x03, 0xeb, 0x17, 0x6f, 0x34, 0x3e, 0x7a, 0x3f, 0xd2, 0xa9, 0x6a, 0x0f, 0xe9, 0x35, 0x56, 0x1f, 0xb1, 0x4d, 0x10, 0x78, 0xd9, 0x75, 0xf6, 0xbc, 0x41, 0x04, 0x81, 0x61, 0x06, 0xf9, 0xad, 0xd6, 0xd5, 0x29, 0x7e, 0x86, 0x9e, 0x79, 0xe5, 0x05, 0xba, 0x84, 0xcc, 0x6e, 0x27, 0x8e, 0xb0, 0x5d, 0xa8, 0xf3, 0x9f, 0xd0, 0xa2, 0x71, 0xb8, 0x58, 0xdd, 0x2c, 0x38, 0x99, 0x4c, 0x48, 0x07, 0x55, 0xe4, 0x53, 0x8c, 0x46, 0xb6, 0x2d, 0xa5, 0xaf, 0x32, 0x22, 0x40, 0xdc, 0x50, 0xc3, 0xa1, 0x25, 0x8b, 0x9c, 0x16, 0x60, 0x5c, 0xcf, 0xfd, 0x0c, 0x98, 0x1c, 0xd4, 0x37, 0x6d, 0x3c, 0x3a, 0x30, 0xe8, 0x6c, 0x31, 0x47, 0xf5, 0x33, 0xda, 0x43, 0xc8, 0xe3, 0x5e, 0x19, 0x94, 0xec, 0xe6, 0xa3, 0x95, 0x14, 0xe0, 0x9d, 0x64, 0xfa, 0x59, 0x15, 0xc5, 0x2f, 0xca, 0xbb, 0x0b, 0xdf, 0xf2, 0x97, 0xbf, 0x0a, 0x76, 0xb4, 0x49, 0x44, 0x5a, 0x1d, 0xf0, 0x00, 0x96, 0x21, 0x80, 0x7f, 0x1a, 0x82, 0x39, 0x4f, 0xc1, 0xa7, 0xd7, 0x0d, 0xd1, 0xd8, 0xff, 0x13, 0x93, 0x70, 0xee, 0x5b, 0xef, 0xbe, 0x09, 0xb9, 0x77, 0x72, 0xe7, 0xb2, 0x54, 0xb7, 0x2a, 0xc7, 0x73, 0x90, 0x66, 0x20, 0x0e, 0x51, 0xed, 0xf8, 0x7c, 0x8f, 0x2e, 0xf4, 0x12, 0xc6, 0x2b, 0x83, 0xcd, 0xac, 0xcb, 0x3b, 0xc4, 0x4e, 0xc0, 0x69, 0x36, 0x62, 0x02, 0xae, 0x88, 0xfc, 0xaa, 0x42, 0x08, 0xa6, 0x45, 0x57, 0xd3, 0x9a, 0xbd, 0xe1, 0x23, 0x8d, 0x92, 0x4a, 0x11, 0x89, 0x74, 0x6b, 0x91, 0xfb, 0xfe, 0xc9, 0x01, 0xea, 0x1b, 0xf7, 0xce]

# def for decoding
def decode_base64_package(base64str):
	# we strip the first 20 chars (SHA1 hash, I don't bother checking it at the moment)
	base64dec = base64.decodestring(base64str)[20:]
	decoded = ''
	for byte in range(0, len(base64dec)):
		decoded += chr(charmap[ord(base64dec[byte])])
	return zlib.decompress(decoded)

# argument parse
parser = argparse.ArgumentParser(description="Oracle .plb packages unwrapper.")
parser.add_argument("-i","--input", help="input package filename",required=True)
parser.add_argument("-o","--output", help="output text filename",required=False)
args = parser.parse_args()

# check
if not os.path.isfile(args.input):
    print "WARNING - Could not find input file."
    sys.exit(1)
    
# options
outfile = None
infile = open(args.input)
if args.output:
	outfile = open(args.output, 'w')

# main
lines = infile.readlines()
if outfile:
    print "Working..."

for i in range(0, len(lines)):
	# this is really naive parsing, but works on every package I've thrown at it
	matches = re.compile(r"^[0-9a-f]+ ([0-9a-f]+)$").match(lines[i])
	if matches:
		base64len = int(matches.groups()[0], 16)
		base64str = ''
		j = 0
		while len(base64str) < base64len:
			j+=1
			base64str += lines[i+j]
		base64str = base64str.replace("\n","")
		if outfile:
			outfile.write(decode_base64_package(base64str) + "\n")
			outfile.close()
		else:
			print(decode_base64_package(base64str))

# file modification
if outfile:
	for line in fileinput.FileInput(args.output,inplace=1):
		if "\x00" in line:
			line = line.replace("\x00","")
                        print line.rstrip()
                else:
                        print line.rstrip()

# check
if outfile:
    if os.path.isfile(args.output):
        print "Done! Output file: " + args.output + "."
    else:
        print "WARNING - Unwrapped package file wasn't created."
        sys.exit(1)
