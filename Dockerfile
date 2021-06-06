
FROM    alpine:latest

# Install Pye'app
# ========================================================
COPY    ./app /app

# Install packages
# ========================================================
RUN     apk add --no-cache libuv python3 py3-pip py3-grpcio py3-lxml py3-pycryptodome \
        && apk add --no-cache --virtual .build-deps build-base python3-dev libuv-dev \
        && pip install --no-cache-dir uvloop \
        && pip install --no-cache-dir -r /app/requirements.txt \
        && apk del .build-deps

# Configure the container
# ========================================================
ENV     PYTHONUNBUFFERED=1
EXPOSE  8080
WORKDIR /app

# Set default runner
# ========================================================
CMD     python3 createAppYaml.py $PYEPASS && unset PYEPASS && /usr/bin/gunicorn -w $WORKER -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 --preload main:app
