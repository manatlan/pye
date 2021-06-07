import zipfile
import os,stat
import io
""" 
    Works with PY3 !!!!!!
    Works with PY3 !!!!!!
    Works with PY3 !!!!!!
    Works with PY3 !!!!!!
    Works with PY3 !!!!!!
"""

def createZip(path):

    def walktree (top = ".", depthfirst = True):
        names = os.listdir(top)
        if not depthfirst:
            yield top, names
        for name in names:
            try:
                st = os.lstat(os.path.join(top, name))
            except os.error:
                continue
            if stat.S_ISDIR(st.st_mode):
                for (newtop, children) in walktree (os.path.join(top, name),
                                                    depthfirst):
                    yield newtop, children
        if depthfirst:
            yield top, names

    list=[]
    for (basepath, children) in walktree(path,False):
          for child in children:
              f=os.path.join(basepath,child)
              if os.path.isfile(f):
                    list.append( f )

    f=io.BytesIO()
    file = zipfile.ZipFile(f, "w")
    for fname in list:
        nfname=os.path.join(os.path.basename(path),fname[len(path)+1:])
        file.write(fname, nfname , zipfile.ZIP_DEFLATED)
        
    db=Files()  
    for id in db.list():
        item=db.get(id)
        content=item["content"]
        file.writestr("files/"+id, content )


    file.close()

    f.seek(0)
    return f
    

try:
    web.response.content_type="application/zip";
    web.response.headers['Content-Disposition']= "attachment; filename=all.zip";	
    return createZip(".").getvalue()
except Exception as e:
    return str(e)

