#!/usr/bin/env python3
import starlette
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.responses import Response,HTMLResponse,RedirectResponse,PlainTextResponse,JSONResponse,StreamingResponse
from fastapi import FastAPI
from starlette.routing import Mount, Route, Router
from starlette.requests import Request

import uvicorn
from libs import guessMimetype

import io,asyncio,os,sys,json,time,glob,traceback,time,datetime,logging,types,base64,fnmatch,codecs,re,pickle,inspect,types,contextlib,hashlib,secrets
import http.cookies
import urllib.parse
from Crypto.Cipher import AES   # pycryptodome

import multiprocessing
SECRET=multiprocessing.Array('c', secrets.token_hex(nbytes=8).encode())

# GLOBAL = multiprocessing.Manager().Namespace() # just to share the secret between process (secret is used for the cookie pass)


__version__="1.20.0"
"""
1.20.1 - fastapi reloaded on second call ;-(
1.20.0 - fastapi backend / uptodate all + reqman2

1.14.3 : compatible new starlette/unicorn (redirect 307, force en 302!)
1.14.2 : prepare the future reqman (reqman.testContent will be async)
1.14.1 : FIX: yielding content was bugged
1.14.0 : set_cookie/delete_cookie !!!
1.13.0 : .rml executed with reqman >= 1.2.0.0 (no rml file are created now on fs, should work on GAE)
1.12.1 : security patch is now robust (works on GAE too!)
1.12.0 : ultra security patch ... cookie.pass change according pye.secret
1.11.5 : revert /authform allows CORS (so can be called xhr from anywhere)
1.11.4 : /authform allows CORS (so can be called xhr from anywhere)
1.11.3 : authent form autocapitalize=off
1.11.2 : authent form autofocus + prevent storing password
1.11.1 : authent form with md5 otp (non replayable by mitm)
         can create (empty)bin file with unknown extension
1.11.0 : otp token (pye.otp / headers["token"])
1.10.0 : rml(reqman.py) & md(mardown2) render to html (rml & md -> good syntax)
1.9.21 : minor gae fix on set admin + pytest 97% coverage
1.9.20 : switch NS according host too, with app.yaml -> cfg["hns"]={}
1.9.16 : without redys !
1.9.15 : clean filemodule importer (no changes !!!) + redys sans deprecating + better tests + avoid 500 recursion
1.9.14 : web and ws are NOT presents in the imported module !
1.9.13 : web and ws are presents in the imported module
1.9.12 : web.isAdmin() & web.request.POST (dict)
1.9.11 : can upgrade starlette, new starlette's path, fix: don't break when no index
1.9.9 : pye inherit of redys
1.9.7 : aware of _STARTUP_/_SHUTDOWN_
1.9.6 : static pye
1.9.5 :
    - great yield/stream all
    - real web.abort(code,txt="")
    - remove pyc/pycache things in fs.list()
    - tests++

1.9.4 - yield -> forget the 1st
1.9.3 - default response to text/html
"""

papp = Starlette()
api = FastAPI() #needed, to be able to declade "@api"


@papp.route("/openapi.json")
def swagger(request):
    return RedirectResponse( "/api/openapi.json" )


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
cfg = { #default config, for the embeded web server
    'host': '0.0.0.0',  #default config, for the embeded web server
    'port': 8080,       #default config, for the embeded web server
    'pass': '630fc37b4123fd1ed0518e3fbd3caa152bd48471d22de03b6f16f6d58ab5e347', # pass = 'pye' (default)
    # also, used too for patcher command (16 first) ^^
    'hns': {},  # dict {host:ns}, ex: {"jbrout.manatlan.com":"jbrout"},
}

try: # update ^cfg^, avec les infos contenus dans le app.yaml !!!
    m=re.search("#(\{.*\})#",open( os.path.join( os.path.dirname(__file__),"app.yaml"),"r").read())
    if m: cfg.update( json.loads(m.group(1)) )
except:
    print("** NO 'app.yaml' (use default conf)")

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

iv=b"098f6bcd4621d373" # the server iv !
pecrypt=lambda x,pw: AES.new(pw, AES.MODE_CFB,iv).encrypt(x)
pdcrypt=lambda x,pw: AES.new(pw, AES.MODE_CFB,iv).decrypt(x)
ecrypt=lambda x: base64.b64encode(pecrypt(pickle.dumps(x,2),bytes(cfg["pass"][:16],"utf8")) ) #encrypt 2
dcrypt=lambda x: pickle.loads(pdcrypt(base64.b64decode(x),bytes(cfg["pass"][:16],"utf8")))
padLeft=lambda b: ("\n".join(["  "+i for i in b.splitlines()]))
md5=lambda x: hashlib.md5(bytes(x,"utf8")).hexdigest()

def normpath(s):
    return os.path.normpath(s).replace("\\","/")

def log(*a):
    pass

isGAE = os.environ.get("GAE_ENV",None) is not None
MAXAGE=3600*24*15 # cookie pass time

if isGAE:
    from libs.app_gae import Files
else:
    from libs.app_fs import Files

def otp(off=0):
    """ OTP token (pass+time)... can get current (off=0) or previous one (off=-1)"""
    assert off==0 or off==-1
    d=datetime.datetime.now()
    d=datetime.datetime(d.year,d.month,d.day,d.hour,d.minute,0)+datetime.timedelta(seconds=off*60)
    return hashlib.md5((str(d)+cfg["pass"]).encode()).hexdigest()

###############################################################################
def isAdmin(request):
    token=request.headers.get("token",None)
    if token:
        return token in [otp(),otp(-1)]
    else:
        return md5(cfg["pass"]+request.headers.get("user-agent","ua")+pye.secret) == request.cookies.get("pass","")

def unauthorized(request):
    url=request.url.path+("?"+request.url.query if request.url.query else "")
    r=RedirectResponse( "/_authform?url=%s" % url )
    r.delete_cookie("pass", path="/")
    return r

###############################################################################


@papp.on_event('startup')
async def on_startup():
    global pye
    print("_STARTUP_")
    # instanciate a pye for the worker
    pye=Pye()

    db=Files()
    f=db.get("_STARTUP_")
    if f:
        #=========================
        code="async def DYNAMIC():\n" + padLeft("pass\n"+f["content"])
        exec( code , globals() )
        await DYNAMIC()
        #=========================

@papp.on_event('shutdown')
async def on_shutdown():
    db=Files()
    print("_SHUTDOWN_")
    f=db.get("_SHUTDOWN_")
    if f:
        #=========================
        code="async def DYNAMIC():\n" + padLeft("pass\n"+f["content"])
        exec( code , globals() )
        await DYNAMIC()
        #=========================



###############################################################################
@papp.route('/_authform',methods=["GET","POST","OPTIONS"])
async def askAuth(request):
    if request.method == "POST":

        url=request.query_params["url"]

        forms=await request.form()
        motp=forms["motp"]
        r=RedirectResponse( urllib.parse.unquote(url), status_code=302 ) #important 302 -> converti en GET (sinon c du 307, ca reste en POST et ca fou la merde)
        if motp == md5(pye.otp):
            r.set_cookie("pass", md5(forms["pw"]+request.headers.get("user-agent","ua")+pye.secret), path="/", max_age=MAXAGE, httponly=True)
            return r
        else:
            r.delete_cookie("pass", path="/")
            return r
    else:
        body= """
        <title>Need authent !</title>
        <meta name="viewport" content="user-scalable=yes, width=device-width, initial-scale=1.0, maximum-scale=1.0" />
        <script>
        /**
        * [js-sha256]{@link https://github.com/emn178/js-sha256}
        *
        * @version 0.5.0
        * @author Chen, Yi-Cyuan [emn178@gmail.com]
        * @copyright Chen, Yi-Cyuan 2014-2017
        * @license MIT
        */
        !function(){"use strict";function t(t,h){h?(c[0]=c[16]=c[1]=c[2]=c[3]=c[4]=c[5]=c[6]=c[7]=c[8]=c[9]=c[10]=c[11]=c[12]=c[13]=c[14]=c[15]=0,this.blocks=c):this.blocks=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],t?(this.h0=3238371032,this.h1=914150663,this.h2=812702999,this.h3=4144912697,this.h4=4290775857,this.h5=1750603025,this.h6=1694076839,this.h7=3204075428):(this.h0=1779033703,this.h1=3144134277,this.h2=1013904242,this.h3=2773480762,this.h4=1359893119,this.h5=2600822924,this.h6=528734635,this.h7=1541459225),this.block=this.start=this.bytes=0,this.finalized=this.hashed=!1,this.first=!0,this.is224=t}var h="object"==typeof window?window:{},i=!h.JS_SHA256_NO_NODE_JS&&"object"==typeof process&&process.versions&&process.versions.node;i&&(h=global);var s=!h.JS_SHA256_NO_COMMON_JS&&"object"==typeof module&&module.exports,e="function"==typeof define&&define.amd,r="undefined"!=typeof ArrayBuffer,n="0123456789abcdef".split(""),o=[-2147483648,8388608,32768,128],a=[24,16,8,0],f=[1116352408,1899447441,3049323471,3921009573,961987163,1508970993,2453635748,2870763221,3624381080,310598401,607225278,1426881987,1925078388,2162078206,2614888103,3248222580,3835390401,4022224774,264347078,604807628,770255983,1249150122,1555081692,1996064986,2554220882,2821834349,2952996808,3210313671,3336571891,3584528711,113926993,338241895,666307205,773529912,1294757372,1396182291,1695183700,1986661051,2177026350,2456956037,2730485921,2820302411,3259730800,3345764771,3516065817,3600352804,4094571909,275423344,430227734,506948616,659060556,883997877,958139571,1322822218,1537002063,1747873779,1955562222,2024104815,2227730452,2361852424,2428436474,2756734187,3204031479,3329325298],u=["hex","array","digest","arrayBuffer"],c=[],p=function(h,i){return function(s){return new t(i,!0).update(s)[h]()}},d=function(h){var s=p("hex",h);i&&(s=y(s,h)),s.create=function(){return new t(h)},s.update=function(t){return s.create().update(t)};for(var e=0;e<u.length;++e){var r=u[e];s[r]=p(r,h)}return s},y=function(t,h){var i=require("crypto"),s=require("buffer").Buffer,e=h?"sha224":"sha256",n=function(h){if("string"==typeof h)return i.createHash(e).update(h,"utf8").digest("hex");if(r&&h instanceof ArrayBuffer)h=new Uint8Array(h);else if(void 0===h.length)return t(h);return i.createHash(e).update(new s(h)).digest("hex")};return n};t.prototype.update=function(t){if(!this.finalized){var i="string"!=typeof t;i&&r&&t instanceof h.ArrayBuffer&&(t=new Uint8Array(t));for(var s,e,n=0,o=t.length||0,f=this.blocks;o>n;){if(this.hashed&&(this.hashed=!1,f[0]=this.block,f[16]=f[1]=f[2]=f[3]=f[4]=f[5]=f[6]=f[7]=f[8]=f[9]=f[10]=f[11]=f[12]=f[13]=f[14]=f[15]=0),i)for(e=this.start;o>n&&64>e;++n)f[e>>2]|=t[n]<<a[3&e++];else for(e=this.start;o>n&&64>e;++n)s=t.charCodeAt(n),128>s?f[e>>2]|=s<<a[3&e++]:2048>s?(f[e>>2]|=(192|s>>6)<<a[3&e++],f[e>>2]|=(128|63&s)<<a[3&e++]):55296>s||s>=57344?(f[e>>2]|=(224|s>>12)<<a[3&e++],f[e>>2]|=(128|s>>6&63)<<a[3&e++],f[e>>2]|=(128|63&s)<<a[3&e++]):(s=65536+((1023&s)<<10|1023&t.charCodeAt(++n)),f[e>>2]|=(240|s>>18)<<a[3&e++],f[e>>2]|=(128|s>>12&63)<<a[3&e++],f[e>>2]|=(128|s>>6&63)<<a[3&e++],f[e>>2]|=(128|63&s)<<a[3&e++]);this.lastByteIndex=e,this.bytes+=e-this.start,e>=64?(this.block=f[16],this.start=e-64,this.hash(),this.hashed=!0):this.start=e}return this}},t.prototype.finalize=function(){if(!this.finalized){this.finalized=!0;var t=this.blocks,h=this.lastByteIndex;t[16]=this.block,t[h>>2]|=o[3&h],this.block=t[16],h>=56&&(this.hashed||this.hash(),t[0]=this.block,t[16]=t[1]=t[2]=t[3]=t[4]=t[5]=t[6]=t[7]=t[8]=t[9]=t[10]=t[11]=t[12]=t[13]=t[14]=t[15]=0),t[15]=this.bytes<<3,this.hash()}},t.prototype.hash=function(){var t,h,i,s,e,r,n,o,a,u,c,p=this.h0,d=this.h1,y=this.h2,l=this.h3,b=this.h4,v=this.h5,g=this.h6,w=this.h7,k=this.blocks;for(t=16;64>t;++t)e=k[t-15],h=(e>>>7|e<<25)^(e>>>18|e<<14)^e>>>3,e=k[t-2],i=(e>>>17|e<<15)^(e>>>19|e<<13)^e>>>10,k[t]=k[t-16]+h+k[t-7]+i<<0;for(c=d&y,t=0;64>t;t+=4)this.first?(this.is224?(o=300032,e=k[0]-1413257819,w=e-150054599<<0,l=e+24177077<<0):(o=704751109,e=k[0]-210244248,w=e-1521486534<<0,l=e+143694565<<0),this.first=!1):(h=(p>>>2|p<<30)^(p>>>13|p<<19)^(p>>>22|p<<10),i=(b>>>6|b<<26)^(b>>>11|b<<21)^(b>>>25|b<<7),o=p&d,s=o^p&y^c,n=b&v^~b&g,e=w+i+n+f[t]+k[t],r=h+s,w=l+e<<0,l=e+r<<0),h=(l>>>2|l<<30)^(l>>>13|l<<19)^(l>>>22|l<<10),i=(w>>>6|w<<26)^(w>>>11|w<<21)^(w>>>25|w<<7),a=l&p,s=a^l&d^o,n=w&b^~w&v,e=g+i+n+f[t+1]+k[t+1],r=h+s,g=y+e<<0,y=e+r<<0,h=(y>>>2|y<<30)^(y>>>13|y<<19)^(y>>>22|y<<10),i=(g>>>6|g<<26)^(g>>>11|g<<21)^(g>>>25|g<<7),u=y&l,s=u^y&p^a,n=g&w^~g&b,e=v+i+n+f[t+2]+k[t+2],r=h+s,v=d+e<<0,d=e+r<<0,h=(d>>>2|d<<30)^(d>>>13|d<<19)^(d>>>22|d<<10),i=(v>>>6|v<<26)^(v>>>11|v<<21)^(v>>>25|v<<7),c=d&y,s=c^d&l^u,n=v&g^~v&w,e=b+i+n+f[t+3]+k[t+3],r=h+s,b=p+e<<0,p=e+r<<0;this.h0=this.h0+p<<0,this.h1=this.h1+d<<0,this.h2=this.h2+y<<0,this.h3=this.h3+l<<0,this.h4=this.h4+b<<0,this.h5=this.h5+v<<0,this.h6=this.h6+g<<0,this.h7=this.h7+w<<0},t.prototype.hex=function(){this.finalize();var t=this.h0,h=this.h1,i=this.h2,s=this.h3,e=this.h4,r=this.h5,o=this.h6,a=this.h7,f=n[t>>28&15]+n[t>>24&15]+n[t>>20&15]+n[t>>16&15]+n[t>>12&15]+n[t>>8&15]+n[t>>4&15]+n[15&t]+n[h>>28&15]+n[h>>24&15]+n[h>>20&15]+n[h>>16&15]+n[h>>12&15]+n[h>>8&15]+n[h>>4&15]+n[15&h]+n[i>>28&15]+n[i>>24&15]+n[i>>20&15]+n[i>>16&15]+n[i>>12&15]+n[i>>8&15]+n[i>>4&15]+n[15&i]+n[s>>28&15]+n[s>>24&15]+n[s>>20&15]+n[s>>16&15]+n[s>>12&15]+n[s>>8&15]+n[s>>4&15]+n[15&s]+n[e>>28&15]+n[e>>24&15]+n[e>>20&15]+n[e>>16&15]+n[e>>12&15]+n[e>>8&15]+n[e>>4&15]+n[15&e]+n[r>>28&15]+n[r>>24&15]+n[r>>20&15]+n[r>>16&15]+n[r>>12&15]+n[r>>8&15]+n[r>>4&15]+n[15&r]+n[o>>28&15]+n[o>>24&15]+n[o>>20&15]+n[o>>16&15]+n[o>>12&15]+n[o>>8&15]+n[o>>4&15]+n[15&o];return this.is224||(f+=n[a>>28&15]+n[a>>24&15]+n[a>>20&15]+n[a>>16&15]+n[a>>12&15]+n[a>>8&15]+n[a>>4&15]+n[15&a]),f},t.prototype.toString=t.prototype.hex,t.prototype.digest=function(){this.finalize();var t=this.h0,h=this.h1,i=this.h2,s=this.h3,e=this.h4,r=this.h5,n=this.h6,o=this.h7,a=[t>>24&255,t>>16&255,t>>8&255,255&t,h>>24&255,h>>16&255,h>>8&255,255&h,i>>24&255,i>>16&255,i>>8&255,255&i,s>>24&255,s>>16&255,s>>8&255,255&s,e>>24&255,e>>16&255,e>>8&255,255&e,r>>24&255,r>>16&255,r>>8&255,255&r,n>>24&255,n>>16&255,n>>8&255,255&n];return this.is224||a.push(o>>24&255,o>>16&255,o>>8&255,255&o),a},t.prototype.array=t.prototype.digest,t.prototype.arrayBuffer=function(){this.finalize();var t=new ArrayBuffer(this.is224?28:32),h=new DataView(t);return h.setUint32(0,this.h0),h.setUint32(4,this.h1),h.setUint32(8,this.h2),h.setUint32(12,this.h3),h.setUint32(16,this.h4),h.setUint32(20,this.h5),h.setUint32(24,this.h6),this.is224||h.setUint32(28,this.h7),t};var l=d();l.sha256=l,l.sha224=d(!0),s?module.exports=l:(h.sha256=l.sha256,h.sha224=l.sha224,e&&define(function(){return l}))}();
        </script>
        <script>
            function trans(f) { f.pw.value = sha256(f.pw.value) }
        </script>
        <style>
        input {
            text-security:disc;
            -webkit-text-security:disc;
            -mox-text-security:disc;
        }
        </style>
        <form method="POST" onsubmit="trans(this)">
            <h3>You are not authorized ;-)</h3>
            <input type="text" name="pw" placeholder="password" autocomplete="off" autocapitalize="none" autocorrect="off" autofocus="true"/>
            <input type="hidden" name="motp" value="%s"/>
            <button>Valid</button>
        </form>
        <script>document.forms[0].pw.focus()</script>
        """ % md5(pye.otp)
        return HTMLResponse(status_code=403, content=body)

###############################################################################
@papp.route('/_logout',methods=["GET"])
async def logout(request):
    r=RedirectResponse( "/" )
    r.delete_cookie("pass", path="/")
    pye._renewSecret() # renew the secret, so all pass'cookies are invalid !
    return r


def getNS(request):
    ns=request.cookies.get("NS","")
    if ns=="":
        ns=cfg["hns"].get( request.headers.get("host","") )
    return ns

###############################################################################
@papp.route("/",methods=["PUT"])
async def patcher(request):
    try:
        commands=dcrypt(await request.body() )
    except Exception as e:
        return JSONResponse({"error":str(e)})

    db=Files( getNS(request) )

    for command in commands:
        try:
            if "set" in command:
                command["return"]=db.set( **command["set"] )
                del command["set"]["content"] # supprime le content pour alleger le retour
            if "delete" in command:
                command["return"]=db.delete( **command["delete"] )

        except Exception as e:
            command["error"] = str(e)

    return JSONResponse({"result": commands})

###############################################################################
#~ @papp.websocket_route("/(?P<path>.*).ws")
@papp.websocket_route("/{path:path}.ws")
async def webSocket(ws):
    path=ws.url.path[1:]

    # set ws.ns !
    #------------------------------
    class WsRequest:
        def __init__(self,ws):
            self.headers=ws.headers
            self.cookies={}
            cookies=http.cookies.SimpleCookie( ws.headers.get("cookie","") )
            if "NS" in cookies:
                self.cookies["NS"] = cookies["NS"].value

    ws.ns= getNS( WsRequest(ws) )
    #------------------------------

    buffer=Files(ws.ns).get(path)["content"]

    #=========================
    code="async def DYNAMIC(ws,__file__):\n" + padLeft("pass\n"+buffer)
    exec( code , globals() )
    await DYNAMIC(ws,path)
    #=========================


###############################################################################
#~ @papp.route("/(?P<path>.*)",methods=["GET","PUT","POST","DELETE","OPTIONS","HEAD"])
@papp.route("/{path:path}",methods=["GET","PUT","POST","DELETE","OPTIONS","HEAD"])
async def main(request):
    path=request.url.path[1:]
    if "|" in path:
        return await concatenate(request,path)
    else:
        return await ressource(request,path)



###############################################################################
###############################################################################
###############################################################################



class Pye:

    @property
    def version(self):
        return "pye %s (%s) (starlette:%s) (uvicorn:%s)" % (__version__,isGAE and "GAE" or "FS",starlette.__version__,uvicorn.__version__)

    @property
    def otp(self):
        return otp()

    @property
    def secret(self):
        return SECRET.value.decode()

    def _renewSecret(self):
        """ invalid secret for all instance/process (so, pass'cookies are all invalid), used by 'GET /_logout' """
        with SECRET.get_lock():
            SECRET.value=secrets.token_hex(nbytes=8).encode()

    def refresh(self):
        """ Purge imported modules starting with 'FILES', just in the current INSTANCE/process """
        modules=list(sys.modules.keys())
        for i in modules:
            if i.startswith("FILES"):
                del sys.modules[i]


class WebWrap:
    def __init__(self,req,body=None):
        def _get_cookie(this,name,defaultValue=None):
            return this.cookies.get(name,defaultValue)
        self.request = req
        self.request.body = body
        self.request.GET = dict(req.query_params)
        try:
            self.request.POST = {k:(v[0] if len(v)==1 else v) for k,v in urllib.parse.parse_qs(body.read().decode()).items()}
            body.seek(0)
        except:
            self.request.POST={}

        self.request.environ = dict(os.environ) # ?!
        self.request.get_cookie = types.MethodType(_get_cookie,req)


        class R:
            def __init__(self,**args):
                self.__dict__.update(args)
                self.sc=[]
                self.dc=[]

            def set_cookie(self,*a,**k):
                self.sc.append( (a,k) )

            def delete_cookie(self,*a,**k):
                self.dc.append( (a,k) )

        self.response = R(status_code=200,headers={},content_type="text/html")

        self._redirectToUrl = None
        self._tasks=[]
        self._abort=None

    def isAdmin(self):
        return isAdmin(self.request)

    @property
    def ns(self):
        return getNS(self.request)

    def redirect(self,url):
        self._redirectToUrl=url

    def abort(self,code,txt=""):
        self._abort=(code,txt)

    def add_task(self,funct,*a,**k):
        self._tasks.append( BackgroundTask(funct,*a,**k) )

    async def _make_the_response(self,r):

        #~ if asyncio.iscoroutine(r):
            #~ r=await r

        async def afterResponse():
            for task in self._tasks:
                await task()

        if self._abort:
            code,txt=self._abort
            x=Response(txt,
                status_code=code,
                headers=self.response.headers or None,
                media_type=self.response.content_type,
                background=BackgroundTask(afterResponse)
            )
        elif self._redirectToUrl:
            x=RedirectResponse( self._redirectToUrl )
        else:

            if hasattr(r,"read"):
                async def readChunk(fid,size):
                    while 1:
                        block = fid.read(size)
                        if block:
                            yield block
                        else:
                            break
                    fid.close()
                r=readChunk(r,size=4096)


            if "async_generator" in str(type(r)): # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                # do the 1st occurence, to set web.response !
                async for i in r:
                    block1=i
                    break

                # and rebuild an async_generator with block 1 and the rest
                async def gegene(block1,r):
                    yield block1
                    async for i in r:
                        yield i

                # and stream them
                x=StreamingResponse( gegene(block1,r) ,
                    status_code=self.response.status_code,
                    headers=self.response.headers or None,
                    media_type=self.response.content_type,
                    background=BackgroundTask(afterResponse)
                )
                for a,k in self.response.sc: x.set_cookie(*a,**k)
                for a,k in self.response.dc: x.delete_cookie(*a,**k)
                return x
            elif type(r) in [list,dict]:                # dict/list -> json
                self.response.content_type="application/json"
                content = json.dumps(r)
            elif type(r)==bytes:                        # bytes     -> bytes
                content = r
            else:
                content = str(r)

            x= Response(content,
                status_code=self.response.status_code,
                headers=self.response.headers or None,
                media_type=self.response.content_type,
                background=BackgroundTask(afterResponse)
            )
        for a,k in self.response.sc: x.set_cookie(*a,**k)
        for a,k in self.response.dc: x.delete_cookie(*a,**k)
        return x
###############################################################################
async def error404(request):
    db=Files( getNS(request) )
    item=db.get("404")
    if not item:
        return Response(status_code=404,content="file not found : %s" % request.url)
    else:
        r=await dynamic(request,item["content"], "404" )
        r.status_code=404
        return r


async def error500(request,error=None):
    db=Files( getNS(request) )
    item=db.get("500")
    if item:
        try:
            r=await dynamic(request,item["content"], "500", error=error )
            if r is not None:   # avoid recursion
                r.status_code=500
                return r
        except Exception as e:
            print("****** the page 500 is bugged:",e)
    return Response(status_code=500,content="SERVER EXCEPTION:\n%s" % error)

async def ressource(request,path,error=None):
    if path=="ed" or path.startswith("ed/"):
        db=Files()
    else:
        db=Files( getNS(request) )
    log("ROUTE : '%s'" % path)

    if path=="" or path.endswith("/"):
        indexes = [i for i in db.list( normpath(os.path.join(path,"*index*")) ) if i.count("/")==path.count("/")]
        if indexes:
            indexes=[i for i in indexes if ("." not in i) or (i.split(".")[-1].lower() in ["htm","html","py"]) ]
            indexes.sort( key=lambda a: a.lower()) # order: ['a/index', 'a/index.htm', 'a/index.html', 'a/index.py']
            path = indexes[0]

    item=db.get(path)

    if not item:    #perhaps path="sitemap.xml" try "sitemap_xml" !
        item=db.get(path.replace(".","_"))

    if item: # trouve le fichier demande

        if item["admin"] and not isAdmin(request):
            return unauthorized(request)

        content     = item["content"]
        timestamp   = item.get("maj",time.time())
        typ         = item.get("type",None)     #could be None on FS pour "index" files

        if (typ and ("python" in typ)) or ("." not in path):    # simple fichier dynamique ("text/python", "application/x-python", ...)
            log("  --> ressource '%s' --> return dynamic" % path)
            return await dynamic(request, content, path, [], error )
        else:
            if path.endswith(".rml"):
                headers={"Content-Type":"text/html; charset=UTF-8"}
                try:
                    import reqman # >= 1.2.0.0
                    m=reqman.testContent( content, {} )
                    if asyncio.iscoroutine(m): m=await m
                    html=m.html
                    headers["rc"]=str(m.code)
                    headers["ok"]=str(m.ok)
                    headers["total"]=str(m.total)
                except Exception as e:
                    html= "Rendering RML trouble : %s" % e
                return Response(status_code=200,content=html,headers=headers)
            elif path.endswith(".md"):
                try:
                    from markdown2 import markdown
                    html = markdown(content)
                except Exception as e:
                    html = content
                return Response(status_code=200,content=html,headers={"Content-Type":"text/html; charset=UTF-8"})
            else:
                log("  --> ressource '%s' --> return static" % path)
                return await static(request, content,str(timestamp),typ )

    else:
        # may be a terminator ?
        paths=path.split("/")
        terminator = paths.pop(0)
        files=db.list( normpath( terminator+"*") )
        while paths:
            if terminator in files: # there is a terminator in the path

                item=db.get(terminator)
                if item["admin"] and not isAdmin(request):
                    return unauthorized(request)

                log("  --> ressource '%s' --> return dynamic terminator for %s %s" % (path,terminator,paths))
                return await dynamic(request, item["content"], terminator, paths, error )

            next=paths.pop(0)
            terminator = normpath(os.path.join(terminator,next))

        # not a terminator, so 404
        log("  --> 404 path '%s'" % path)
        return await error404(request)


async def concatenate(request,path):
    ll=[i.strip() for i in path.split("|")]
    f=ll.pop(0) # first ressource set the path for the others

    multiples=[f]
    for i in ll:
        if i.startswith("/"):
            multiples.append( i[1:] ) # remove "/"
        else:
            multiples.append( normpath( os.path.dirname(f) and "/".join( [os.path.dirname(f),i] ) or i ) ) # append default folder

    db=Files( getNS(request) )

    buffers=[]
    etag=""
    for path in multiples:
        item=db.get(path)
        if not item:
            return await error404(request)    # don't find a file in the concatenation suite
        else:
            if item["admin"] and not isAdmin(request):
                return unauthorized(request)

            content     = item["content"]
            timestamp   = item.get("maj",time.time())
            typ         = item.get("type",None)

            if "python" in typ:
                return await error404(request)  # python file are not visible in concatenate static context ;-)
                                                #TODO: renderate & and stream !

            etag+=str(timestamp)
            buffers.append(content)

    return await static(request,"\n".join(buffers),etag,typ)    # the type of the last file


async def static(request,buffer,etag,typ=None):
    etag=md5(etag)
    rheaders={}
    if typ: rheaders["Content-Type"] = typ+"; charset=UTF-8";

    rheaders["etag"]= etag;
    if etag!=request.headers.get("if-none-match",None):
        return Response(status_code=200,content=buffer,headers=rheaders)
    else:
        return Response(status_code=304,headers={"Content-Length":"0"})

async def dynamic(request,buffer, path, argv=[],error=None ):
    if callable(request.body):
        body=io.BytesIO(await request.body())
    else:
        body=request.body
    try:
        web=WebWrap(request,body)
        #==================================================================
        stdout=io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code="async def DYNAMIC(web,__file__,argv,error):\n" + padLeft("pass\n"+buffer)
            exec( code , globals() )
            r = DYNAMIC(web,path,argv,error)
            r = await r if asyncio.iscoroutine(r) else r

        if r==None: r=stdout.getvalue()
        #==================================================================
        return await web._make_the_response( r )
    except Exception as e:
        if error==None:
            return await error500(request,error=traceback.format_exc())
        else:
            #avoid recursion, coz it's already an error
            return None
#################################################################################################
## Importer (from FILE import fichier)
#################################################################################################
import sys,os
import importlib,types

class FileImportFinder: # http://dangerontheranger.blogspot.com/2012/07/how-to-use-sysmetapath-with-python.html
    def find_module(self, fullname, path = None):
        return self if fullname.startswith("FILE") else None
    def load_module(self, fullname):
        if fullname in sys.modules:
            m=sys.modules[fullname]
        else:
            m = types.ModuleType(fullname)
            m.__file__ = fullname
            m.__path__ = []
            m.__loader__ = self
            m.Files=Files
            m.pye=pye

            mm=fullname.split(".")
            if len(mm)>1:
                if "_" in mm[0]: # from FILES_xxx.libs ...
                    ns=mm[0].split("_")[-1]
                else:
                    ns=None
                path="/".join(mm[1:])

                db=Files(ns)
                item=db.get( path+".py" )
                if item:
                    #~ m._importedMaj=item["maj"]
                    try:
                        exec( item["content"],m.__dict__)   # !!!!!!!!!!!!!
                    except Exception as e:
                        raise ImportError("Can't import %s : %s"% (fullname,e))
                else:
                    folder=path+"/"
                    all=[i[:len(folder)] for i in db.list()]
                    if folder not in all:
                        raise ImportError("Can't import '%s' : not found"% (fullname))
            else:
                m.refresh=pye.refresh #DEPRECATED (use pye.refresh())

            sys.modules[fullname]= m

        return m


my=FileImportFinder()
# insert le finder dans le metapath
for idx,importer in enumerate(sys.meta_path):
    if importer.__class__.__name__ == my.__class__.__name__:
        del sys.meta_path[idx]
        break
sys.meta_path.append(my)
############################################


class PyeWithAPI(Router):
    def __init__(self,pyeApp):
        Router.__init__(self,[
            Mount('/api', app=api),
            Mount('/', app=pyeApp),
        ])

        fapi=Files().get("api")
        if fapi:
            self.reloadAPI(fapi["content"])

        self.lifespan = pyeApp.router.lifespan


    def reloadAPI(self,content):
        global api
        api=FastAPI() #reload (needed!)

        @api.middleware("http")
        async def reloadProcess(request: Request, call_next):
            db=Files()
            try:
                self.reloadAPI( db.get("api")["content"] )
                err="ok"
            except Exception as e:
                err=str(e)
            response = await call_next(request)
            response.headers["X-api-reloaded"] = err
            return response

        try:
            exec(content)
            mapi=Mount("/api",app=api)
            for idx,i in enumerate(self.routes):
                if i.path=="/api":
                   logging.info("Reload FastAPI '/api'")
                   self.routes[idx] = mapi

        except Exception as e:
            logging.error("reloadAPI(): %s" % e)
            raise e

app = PyeWithAPI(papp)
#~ app = papp




if __name__=="__main__":
    app.debug=True
    uvicorn.run(app, host=cfg["host"], port=int(cfg["port"]))
