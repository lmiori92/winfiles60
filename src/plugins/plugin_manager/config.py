#Plugin configuration reader

_comment = [';','#']
_config_dict = {"version"

class Reader:

    def __init__(s, file):
    
        s.file = file

    def read(s):
    
        f = open(s.file,'rb')
        buf = "!"
        while buf:
            buf = f.readline()
            start_char = buf[0]
            #Comment
            if start_char in _comment:
                continue
            l = buf.split('=',1)
            if len(l)!=2:
                print "Invalid configuration line!", buf
            else:
                property = l[0]
                value = l[1]
                
                
    def parse_config(s, p, v):
        
        