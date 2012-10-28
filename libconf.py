import os
import re

def totuple(string):
	## Returns tuple represented by /string/.
	return tuple(map(int, string[1:-1].split(',')))

def tobool(string):
	## Returns bool represented by /string/.
	if string[0].lower() == 't':
		return True
	else:
		return False

def totext(resolution=(400,300), fullscreen=True, path=os.environ['HOME']+'/Pictures/', recursive=True, music=os.environ['HOME']+'/Music/', order=False, delay=5, transition='Superimposition'):
	## Saves settings to text.
	print order
	homePath = os.getenv('HOME')
	print '\nSaving settings to ' + homePath + '/.ppslideshow'
	configfile = open(homePath + '/.ppslideshow', 'w')
	configfile.write(
		'Resolution:    ' + str(resolution) +
		'\nFullscreen:    ' + str(fullscreen) +
		'\nPath:          ' + path +
		'\nRecursive:     ' + str(recursive) +
		'\nMusic:         ' + music +
		'\nOrder:         ' + str(order) +
		'\nDelay:         ' + str(delay) +
		'\nTransition:    ' + transition)
	configfile.close()
	configfile = open(homePath + '/.ppslideshow', 'r')
	print configfile.read()
	configfile.close()

def fromtext():
	## Loads settings from text.
	homePath = os.getenv('HOME')
	configfile = open(homePath + '/.ppslideshow', 'r')
	configtext = configfile.read()
	configfile.close()
	config = {}
	print '\nLoading settings from ' + homePath + '/.ppslideshow'
	print configtext
	for line in re.split('\n', configtext):
		data = re.split(':\s*', line)
		config[data[0]] = data[1]
	try:
		return totuple(config['Resolution']), tobool(config['Fullscreen']), config['Path'], tobool(config['Recursive']), config['Music'], tobool(config['Order']), float(config['Delay']), config['Transition']
	except:
		print 'ERROR: Failed to retrieve settings!'
