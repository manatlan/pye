import os, mimetypes


def guessMimetype(path): # nearly the same as in index.html
    fn=os.path.basename(path).lower()
    if "." not in fn:
        return "text/python"
    else:
        if  fn.endswith(".js"): return "text/javascript"
        elif fn.endswith(".jsm"): return "text/javascript"
        elif fn.endswith(".html"): return "text/html"
        elif fn.endswith(".htm"): return "text/html"
        elif fn.endswith(".tpl"): return "text/html"
        elif fn.endswith(".tags"): return "text/html"
        elif fn.endswith(".tag"): return "text/html"
        elif fn.endswith(".vue"): return "text/html"
        elif fn.endswith(".xml"): return "text/xml"
        elif fn.endswith(".xsl"): return "text/xml"
        elif fn.endswith(".xslt"): return "text/xml"
        elif fn.endswith(".css"): return "text/css"
        elif fn.endswith(".py"): return "text/python"
        elif fn.endswith(".ws"): return "text/python"       # websocket
        elif fn.endswith(".txt"): return "text/plain"
        elif fn.endswith(".log"): return "text/plain"
        elif fn.endswith(".json"): return "text/json"
        elif fn.endswith(".yml"): return "text/yaml"
        elif fn.endswith(".yaml"): return "text/yaml"
        elif fn.endswith(".rml"): return "text/yaml"    #new
        elif fn.endswith(".lua"): return "text/lua"
        elif fn.endswith(".ini"): return "text/ini"
        elif fn.endswith(".cfg"): return "text/ini"     
        elif fn.endswith(".conf"): return "text/ini"    
        elif fn.endswith(".md"): return "text/markdown"    
        elif fn.endswith(".rst"): return "text/markdown"    
        else:
            return mimetypes.guess_type(path)[0] or "unknown"
