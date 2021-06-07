# pye

## It's out ;-)

As a [docker image](https://hub.docker.com/r/manatlan/pye) !

**pye** is basically a "web editor" to dev "web things" (with python3) online. It's a ASGI thing, using uvloop+gunicorn. (it's between [appJet](https://en.wikipedia.org/wiki/AppJet) and [glitch.com](https://glitch.com) .... focused on python3/async, see at the bottom)

Unittests(97%cov) + docs will come later

### Using [docker-hub image](https://hub.docker.com/r/manatlan/pye) :

#### Just try

    sudo docker run -p 8111:8080 -e PYEPASS=test -e PYEWORKER=1 manatlan/pye

And go to [http://localhost:8111/ed](http://localhost:8111/ed), enter "test"+RETURN, you are in the editor/admin place, and
can do all what you want. But keep in mind, that everything you edit/create will disapear after stoping the instance.

#### Go further, IRL

    sudo docker run -p <<YOUR_PORT>>:8080 -v <<YOUR_FILES_FOLDER>>:/app/files -e PYEPASS=<<YOUR_PASSWORD>> -e PYEWORKER=<<YOUR_NB_OF_WORKERS>> manatlan/pye

If "YOUR_FILES_FOLDER" folder is empty, first run will fill it with defaults one (tutorial + edit'or + tests)
In this case, all modifications will be in your filesystem. It's a lot better ;-)


### Using the Dockerfile / [github repo](https://github.com/manatlan/pye)


#### to build :

    ./build

#### to test :

    ./run

    And you can surf to :

        - http://localhost:12345/
        - http://localhost:12345/ed  (with pass "test")


#### to use in production :

    sudo docker run -p <<YOUR_PORT>>:8080 -v <<YOUR_FILES_FOLDER>>:/app/files -e PYEPASS=<<YOUR_PASSWORD>> -e WORKER=<<YOUR_NB_OF_WORKERS>> pye


#### to visit the container :

    ./connect



## ORIGINAL readme.md (from the past)

A (web) PYthon Engine ... to developp websites in websites ;-)

Basically, it operates in the HTTP part, by handling HTTP requests. Between the client and the filesystem (or db). If the http request address a static file, **pye** will return the static file, if the http request adress a dynamic/python file, **pye** will return the execution of this dynamic file. That's all.

BUT ... with a special dynamic file, called "ed", the http response will be a full featured online editor, which will let the user edit its files online, thru a web browser (desktop or mobile). "ed" is just like any files, but you can access and edit your server, thru a simple web browser.

"ed" can be edited thru "ed", and be adapted to your needs ... but **pye** comes with many tricks, that handle a lot of things (admin access, import statement, path resolvers, 304 responses, concatenate files, post processing, 404 & 500 handlers, ...)

BTW, **pye** is designed to work on GoogleAppEngine 2nd Generation (python37), or any hosts that provides python3.

... __to be continued__ ...


