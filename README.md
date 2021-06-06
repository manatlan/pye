# pye

## It's out ;-)

Due to the complexity of setuping all, **pye** was never released before ;-)

But with the facility of docker : I reach to make something that is (pretty) usable (in prod too) ;-)

**Currently**, it's just the DockerFile with the pye's app -> it's the github account,
to build the docker's image ! But the image will be available in the docker-hub too,
and I will make more docs and add all my code coverage tests (97%) ... and some docs ;-)

### TO BUILD :

    ./build

### TO TEST :

    ./run

    And you can surf to :

        - http://localhost:12345/
        - http://localhost:12345/ed  (with pass "test")


### TO USE IN PRODUCTION :

    sudo docker run -p <<YOUR_PORT>>:8080 -v <<YOUR_FILES_FOLDER>>:/app/files -e PYEPASS=<<YOUR_PASSWORD>> -e WORKER=<<YOUR_NB_OF_WORKERS>> pye


### TO CONNECT to the container :

    ./connect



## ORIGINAL readme.md (from the past)

A (web) PYthon Engine ... to developp websites in websites ;-)

Basically, it operates in the HTTP part, by handling HTTP requests. Between the client and the filesystem (or db). If the http request address a static file, **pye** will return the static file, if the http request adress a dynamic/python file, **pye** will return the execution of this dynamic file. That's all.

BUT ... with a special dynamic file, called "ed", the http response will be a full featured online editor, which will let the user edit its files online, thru a web browser (desktop or mobile). "ed" is just like any files, but you can access and edit your server, thru a simple web browser.

"ed" can be edited thru "ed", and be adapted to your needs ... but **pye** comes with many tricks, that handle a lot of things (admin access, import statement, path resolvers, 304 responses, concatenate files, post processing, 404 & 500 handlers, ...)

BTW, **pye** is designed to work on GoogleAppEngine 2nd Generation (python37), or any hosts that provides python3.

... __to be continued__ ...


