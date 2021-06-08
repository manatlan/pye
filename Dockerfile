
FROM    alpine:latest

ENV     PYEFOLDER=/app

# Install Pye'app
# ========================================================
COPY    ./app $PYEFOLDER

# Install packages
# ========================================================
RUN     apk add --no-cache libuv python3 py3-pip py3-lxml py3-pycryptodome py3-yarl \
        && apk add --no-cache --virtual .build-deps build-base python3-dev libuv-dev \
        && pip install --no-cache-dir uvloop \
        && pip install --no-cache-dir -r $PYEFOLDER/requirements.txt \
        && apk del .build-deps

# Configure the container
# ========================================================
ENV     PYTHONUNBUFFERED=1
EXPOSE  8080
WORKDIR $PYEFOLDER

# Set default runner
# ========================================================
CMD     python3 initpye.py $PYEPASS && unset PYEPASS && /usr/bin/gunicorn -w $PYEWORKERS -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 --preload main:app
