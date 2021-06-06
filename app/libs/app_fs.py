import sys, os, codecs, urllib, fnmatch, hashlib, json
from . import guessMimetype

EFS = sys.getfilesystemencoding()
def u(s):
    return s

class XAdmins(list): # extended attributes for managae admin files
    def __init__(self, rootdir):
        self.file = os.path.join(rootdir, "_adminFiles.json")
        if os.path.isfile(self.file):
            with open(self.file, "r+") as fid:
                ll = sorted(json.load( fid ))
        else:
            ll = []
        list.__init__(self, ll)

    def add(self, path):
        if path not in self:
            self.append(path)
            with open(self.file, "w+") as fid: json.dump( list(self), fid )

    def sub(self, path):
        if path in self:
            del self[ self.index(path) ]
            with open(self.file, "w+") as fid: json.dump( list(self), fid )

class Files():
    path=os.path.join( os.path.dirname(__file__),"..") # should exist !

    def __init__(self,ns=None):
        self.ns=ns
        self._files=os.path.join( Files.path, "files"+("."+ns if ns else "") )

        self.admins=XAdmins(self._files)

    def list(self,match=None,admin=None):
        norm=lambda x: u(x[len(self._files)+1:].replace("\\","/"))
        ll=[norm(os.path.join(base,f)) for base, _, files in os.walk(self._files) if not base.endswith("__pycache__") for f in files if not f.endswith(".pyc")]
        af=os.path.basename(self.admins.file)
        if af in ll: del ll[ ll.index(af) ]
        if match: ll=fnmatch.filter(ll,match)
        if admin is not None:
            if admin is True:
                ll=[i for i in ll if i in self.admins]
            else:
                ll=[i for i in ll if i not in self.admins]

        return sorted(ll)


    def set(self,id,content=None,typ=None,admin=None):
        assert os.path.basename(id)
        if content is None and typ is None:
            assert admin is not None
            fp=os.path.join( self._files,id)
            if os.path.isfile(fp):
                if admin:
                    self.admins.add( id )
                else:
                    self.admins.sub( id )
                return True #admin changed
        else:
            fp=os.path.join( self._files,id)
            if not os.path.isfile(fp):
                d=os.path.dirname(fp)
                if not os.path.isdir(d):
                    os.makedirs(d)

            if not typ: typ=guessMimetype(fp)

            if typ and typ.startswith("text"):
                with codecs.open(fp, "w+", EFS) as fid:
                  if hasattr(content,"decode"):
                    try:
                      fid.write( content.decode("UTF-8") )
                    except:
                      fid.write( content.decode("cp1252") )
                  else:
                    fid.write( content )
            else:
                with open(fp, "wb+") as fid:                    # save as binary
                    if type(content)==bytes:
                        fid.write( content )
                    else:
                        fid.write( content.encode() )

            if admin is not None:
                if admin:
                    self.admins.add( id )
                else:
                    self.admins.sub( id )

            return typ

    def get(self,id):
        fp=os.path.join( self._files,id)
        if os.path.isfile(fp):
            typ=guessMimetype(fp)
            if typ and typ.startswith("text"):
                with codecs.open(fp, "r", EFS) as fid:
                    content=fid.read()
            else:
                with open(fp,"rb") as fid:
                    content=fid.read()
            return {
                "content":content,
                "type":typ,
                "maj":os.stat(fp).st_mtime,
                "admin": True if id in self.admins else False,
            }
        else:
            return None

    def delete(self,id):
        fp=os.path.join( self._files,id)
        if os.path.isfile(fp):
            os.unlink(fp)
            try:
                os.removedirs( os.path.dirname(fp) )
                os.makedirs(Files.path)
            except:
                pass
            self.admins.sub(id)
            return True
        else:
            return False

    @staticmethod
    def namespaces():
        ll=[]
        for i in os.listdir(Files.path):
            if i.startswith("files."):
                ll.append( i.split(".",1)[1])
        return ll
