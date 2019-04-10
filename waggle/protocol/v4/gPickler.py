# ANL:waggle-license
# This file is part of the Waggle Platform.  Please see the file
# LICENSE.waggle.txt for the legal details of the copyright and software
# license.  For more details on the Waggle project, visit:
#          http://www.wa8.gl
# ANL:waggle-license
'''
This module contians compression utilities intended to put objects into a format
sendable through waggle.
'''
import pickle as Pickle
from zlib import compress, decompress

def gPickle(data):
	"""
		Returns a gPickled representation of any information sent to it.

		:param object data: The sensor data to gPickle
		:rtype: string
	"""
	return compress(Pickle.dumps(data, protocol=2))

def un_gPickle(data):
	"""
	    Given some gPickled data, restores it to its original form.

	    :param string data: The data to be un gPickled
	    :rtype: object
	"""
	return Pickle.loads(decompress(data))
