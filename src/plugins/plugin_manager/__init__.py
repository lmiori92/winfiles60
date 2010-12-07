#WinFile Plugin Manager

module_version = 0.1
debug = 1

print "Loading plugin manager..."
from plugins import manager
print "Loading plugin loader..."
from plugins import loader