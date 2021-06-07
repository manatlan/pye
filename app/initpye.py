#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import os,sys,re,hashlib,shutil

"""
INIT the instance config !

    - create an app.yaml with the pass.

"""


def createAppYaml(pwd):
    """

    An original "app.yaml" was like that (here for py3 app engine):

    '''
        runtime: python37
        instance_class: F2
        entrypoint: gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b :$PORT --preload main:app
        ###{"host":"0.0.0.0","port":8080,"pass":"64439b97a2d21e6fd22a07d14924c449aeba88e1ab4f60ec0278191eeb5bae83"}###
    '''

    It was mainly used on "google app engine" (it's the file to describe the instance)
    But this file could be used outside of GAE too.
    And the "infos" was stored in a JSON, in a yaml comment ;-)
    (So things could works OOTB, just by moving all)

    (Historically, the admin access was accorded to the admin GAE account.)
    (this "json in yaml comment" was just a trick to make it works outside of gae.)

    """
    shaPass=hashlib.sha256(pwd.encode()).hexdigest()
    with open("app.yaml","w+") as fid:
        fid.write("""###{"host":"0.0.0.0","port":8080,"pass":"%s"}###""" % shaPass)
    print("* app.yaml created")


def fillFilesFolder():
    """ mechanism to fill the 'files/' folder with some default files
        (like 'ed' ... which can be useful ootb ;-)
    """
    if os.path.isdir("files"):
        files = os.listdir("files")
    else:
        files=[]

    if not files:
        shutil.copytree("files_default/","files/",dirs_exist_ok=True)
        print("* Fill 'files/' folder with defaults one")
    else:
        print("* The 'files/' folder contains already something, leave it as is")


if __name__=="__main__":
    # ensure that we are in the pwd
    try:
        os.chdir(os.path.split(sys.argv[0])[0])
    except:
        pass

    if len(sys.argv)==2:
        createAppYaml( sys.argv[1] )
        fillFilesFolder()
        sys.exit(0)
    else:
        print("USAGE: initpye.py <pwd>")
        sys.exit(-1)
