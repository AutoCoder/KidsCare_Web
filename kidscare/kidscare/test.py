import os
import sys

filename = os.path.join(os.path.dirname(__file__),'winlogoff.wav')
f = open(filename, 'rb')
content = f.read()
print "size %s" % sys.getsizeof(content)