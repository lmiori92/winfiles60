'''

The idea is to join graphics files loading and theme colors loading, in order to load everything at winfile start.
This is not only better to avoid bugs, but in order to define other usefull definitions like: some renamed files, different mask size, no mask support etc...

15/07/2010
'''

class SknInfo:
    def __init__(s, skn):
        s.skin_path=skn
        s.name=''
        s.author=''
        s.version=0.0
        s.description=''
        s.docpath=None
        s.winfile_version=1.054

class Theme_Handler(object):
    skn_begin="WF_SKIN_FILE_BEGIN"
    skn_end="WF_SKN_FILE_END"

    
    def load(s):
        fo = open( s.skin_path, 'rb' , 100)
        if fo.read(len(skn_begin))!=skn_begin:
            raise "Invalid skin file: invalid header"
        if fo.read(-len(skn_end), 2)!=skn_end:
            raise "Invalid skin file: truncated file"
        