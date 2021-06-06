#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import os,sys,re,hashlib

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

(At the beginning, the admin access was accorded to the admin GAE account.)


to keep things, this script is just used to recreate a app.yaml with the pass.

"""


def build(pwd):
    shaPass=hashlib.sha256(pwd.encode()).hexdigest()
    with open("app.yaml","w+") as fid:
        fid.write("""###{"host":"0.0.0.0","port":8080,"pass":"%s"}###""" % shaPass)

if __name__=="__main__":
    if len(sys.argv)==2:
        build( sys.argv[1] )
        print("app.yaml created")
        sys.exit(0)
    else:
        print("USAGE: createAppYaml.py <pwd>")
        sys.exit(-1)
