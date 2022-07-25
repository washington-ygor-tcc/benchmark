import asyncio
import sys
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError


async def main(loop):
    print("aa")
    try:
        nc = await nats.connect("0.0.0.0:4222")
    except Exception as e:
        print("a")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        sys.stdout.write("*")
        sys.stdout.flush()
        print(
            "Received a message on '{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data
            )
        )

    # Simple publisher and async subscriber via coroutine.
    sub = await nc.subscribe("foo", cb=message_handler)

    # Stop receiving after 2 messages.
    await sub.unsubscribe(10)
    await nc.publish("foo", b"Hello")
    await nc.publish("foo", b"World")
    await nc.publish("foo", b"!!!!!")

    print("b")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
    loop.close()
