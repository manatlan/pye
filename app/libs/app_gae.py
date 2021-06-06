from google.cloud import datastore


import time,os,socket
import fnmatch

from . import guessMimetype


class Files():
    def __init__(self,ns=None): # namespace
        if ns:
            self.ns=ns
        else:
            self.ns=None
        self.client = datastore.Client(namespace=self.ns)

    def _key(self,id):
        #~ assert os.path.basename( str(id) )
        return self.client.key('File', str(id) )

    def list(self,match=None,admin=None):
        query = self.client.query(kind="File")
        query.keys_only()

        if admin is not None:
            if admin:
                query.add_filter('admin', '=', True)
            else:
                query.add_filter('admin', '=', False)

        liste = list([entity.key.name for entity in query.fetch()])
        if match:
            return fnmatch.filter(liste,match)
        else:
            return liste

    def set(self,id,content=None,type=None,admin=None):
        assert os.path.basename(id)
        with self.client.transaction():
            key = self._key(id)

            item = self.client.get(key)
            new=None
            if item is None:
                new = datastore.Entity(key=key,exclude_from_indexes=['content',"bin"])
                item={}

            if content is None and type is None:
                assert admin in [False,True]
                if item=={}: return None
                item["admin"]=admin
                item["maj"]=time.time()
                ret=True
            else:
                if not type: type=guessMimetype(id)

                if admin is not None:
                    item["admin"]=admin
                item["type"]=type
                if type and type.startswith("text/"):
                    if hasattr(content,"decode"):
                        try:
                          item["content"]=str(content,"utf8")
                        except:
                          item["content"]=str(content,"cp1252")
                    else:
                          item["content"]=content

                else:
                    item["bin"]=content    # !!!!!!!!!!!!!!!!!!!!!!!!!!!
                item["maj"]=time.time()
                ret=type


            if new is not None:
                new.update(item)
                item=new
            self.client.put(item)
            return ret

    def get(self,id):
        id=str(id) ##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if id:
            i= self.client.get( self._key( id) )
            if i:
                return {
                    "content":i["content"] if ("type" in i) and i["type"].startswith("text/") else i["bin"],
                    "type":i["type"],
                    "maj":i["maj"],
                    "admin": i["admin"] if "admin" in i else False
                }


    def delete(self,id):
        assert os.path.basename(id)
        self.client.delete( self._key( id) )
        return True

    @staticmethod
    def namespaces():
        query = datastore.Client().query(kind='__namespace__')
        query.keys_only()
        return [entity.key.name for entity in query.fetch() if entity.key.name]
