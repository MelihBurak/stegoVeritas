#!/usr/bin/python3

from PIL import Image
import subprocess
import binascii
import os, os.path
import time
import shutil

# Get our current dir
CWD = os.path.dirname(os.path.realpath(__file__))

TEMPFILE = os.path.join(CWD,"stegodone.temp")
# TODO: Use python to make this dynamic
RESULTSDIR = os.path.join(CWD,"results")

# Make the folder if need be
os.makedirs(RESULTSDIR,exist_ok=True)

# Load the image
f = Image.open("blind")

def _dumpLSB(img,index):
	"""
	Mostly obsolete since extraction method changed
	Input:
		img == PIL image (type PIL.Image.Image)
		index == integer from LSB to extract (0 == first bit, 1 == second bit, etc)
	Action:
		Extract array of bits represented as integers
	Returns:
		Bit integer array (i.e.: [0,1,1,0,0,1,0,1 ...]
	"""
	# Make sure we're working with the right thing
	if type(img) != Image.Image:
		raise Exception("_dumpLSB: image type should be PIL.Image.Image.\nActual image type is {0}".format(type(img))) 
	
	# Check index
	if index >= 8:
		raise Exception("_dumpLSB: index cannot be >= 8.\nActual index is {0}".format(index))
	
	# Perform bit extraction
	out = [str((byte >> index) & 1) for byte in img.tobytes()]
	
	return out

# Change this to a primitive to dump any given index of a given color
# Then, handle the weaving of those together in a different function
def _dumpLSBRGBA(rIndex = [],gIndex = [],bIndex = [],aIndex = []):
	"""
	Input: 
		rIndex, gIndex, bIndex, aIndex as array of integer indexes (up to 8) to dump
		ex: [0],None,None would dump only the least significant bit of the Red field
	Action:
		Creates a byte array containing the output of the LSB dump (RGBA order) requested
		If needed, it will use the least significant bit first, then bit plane order of red->green->blue->alpha
	Returns:
		Byte array of the result of the action
		ex: b'\x01\x02\x03\x04' etc
	"""
	
	##################
	# Combine Output #
	##################
	# We'll be keeping the binary string here
	binStr = ''

	# Figure out valid index ranges
	indexes = list(set(rIndex + gIndex + bIndex + aIndex))
	indexes.sort()
	
	# Figure out what we have to work with
	bands = f.getbands()
	
	# Get the image bytes
	fBytes = f.tobytes()
	
	# TODO: The following assumes an ordering of RGBA. If this is ever not the case, things will get mixed up
	# Loop through all the bytes of the image
	for byte in range(0,f.size[0] * f.size[1] * len(bands),len(bands)):
		# Loop through all the possible desired indexes
		for index in indexes:
			# If this is a value we're extracting
			if index in rIndex:
				binStr += str(fBytes[byte + 0] >> index & 1)
			if index in gIndex:
				binStr += str(fBytes[byte + 1] >> index & 1)
			if index in bIndex:
				binStr += str(fBytes[byte + 2] >> index & 1)
			if index in aIndex:
				binStr += str(fBytes[byte + 3] >> index & 1)
	
	# Parse those into bytes
	bArray = []
	for i in range(0,len(binStr),8):
		bArray.append(int(binStr[i:i+8],2))
	
	# Change bytes into a bit array for writing
	bits = ''.join([chr(b) for b in bArray]).encode('iso-8859-1')
	
	return bits

def testOutput(b):
	"""
	Input:
		b = byte array output, generally from the dump functions
		ex: b = b'\x01\x02\x03'
	Action:
		Test if output is worth keeping.
		Initially, this is using the Unix file command on the output and checking for non "Data" returns
	Return:
		Nothing. Move output into keep directory if it's worth-while	
	"""

	# Write out the buffer	
	temp = open(TEMPFILE,"wb")
	temp.write(b)
	temp.close()
	
	# Run the file command
	out = subprocess.check_output(["file",TEMPFILE])
	
	# We like anything that's not just data
	if b': data\n' not in out:
		print("Found something worth keeping!\n{0}".format(out))
		shutil.move(TEMPFILE,os.path.join(RESULTSDIR,str(time.time())))

	try:
		# Remove our mess
		os.unlink(TEMPFILE)
	except OSError:
		pass


#o = _dumpLSBRGBA(bIndex=[1,2,3],gIndex=[1],aIndex=[0])
#print(o)
#exit()

for r in range(0,3):
	for g in range(0,3):
		for b in range(0,3):
			print("Trying {0}.{1}.{2}".format(r,g,b))
			o = _dumpLSBRGBA(rIndex=[r],gIndex=[g],bIndex=[b])
			testOutput(o)


# m = magic.Magic(magic.MAGIC_MIME)
# subprocess.check_output(["file","CoolPic.png"])
# subprocess.check_output("file *",shell=True)

# find . -maxdepth 1 -type f -exec binwalk -eM {} \;

