await ws.accept()
from FILES.websocket.lib import text

while 1:
    data = await ws.receive_text()
    await ws.send_text("I am "+text()+", you send me '%s' (you are X)" % (data))

await ws.close()