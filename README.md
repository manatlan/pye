# pye
A (web) PYthon Engine ... to developp websites in websites ;-)

Basically, it operates in the HTTP part, by handling HTTP request. Between the client and the filesystem (or db). If the http request address a static file, **pye** will return the static file, if the http request adress a dynamic/python file, **pye** will return the execution of this dynamic file. That's all.

BUT ... with a special dynamic file, called "ed", the http response will be a full featured online editor, which will let the user edit its files online, thru a web browser (desktop or mobile). "ed" is just like any files, but you can access and edit your server, thru a simple web browser.

"ed" can be edited thru "ed", and be adapted to your needs ... but **pye** comes with many tricks, that handle a lot of things (admin access, 304 responses, concatenate files, post processing, ...)

BTW, **pye** is designed to work on GoogleAppEngine 2nd Generation (python37), or any hosts that provides python3.

... __to be continued__ ...
