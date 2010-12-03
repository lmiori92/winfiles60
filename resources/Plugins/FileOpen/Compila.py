import py_compile,os,sys
path=sys.path[1]
print path
for file in os.listdir(path):
    if os.path.splitext(file)[1]==".py":
        py_compile.compile(os.path.join(path,file))
        print file," compilato correttamente!"

print "Fine"