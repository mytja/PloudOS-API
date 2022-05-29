# PloudOS-API
An unofficial API for PloudOS.

This library contains a lot of functions and is fully asynchronous.

# Example
```py
import asyncio
from ploudos import PloudOS

myserverid = 0
ploudos = PloudOS("myusername", "mypassword", myserverid)

async def main():
    await ploudos.login()
    info = await ploudos.get_server_info()
    if info.get("isRunning") is True and info.get("isStarted") is True:
        # It's already started and running
        return
    print(info)
    cr = await ploudos.can_restart()
    print(cr)
    if cr:
        await ploudos.restart()
    else:
        q = await ploudos.queue()
        if q:
            print("Server accepting is necessary. Executing the command.")
            await ploudos.accept_server()
    print(await ploudos.get_server_info())
    await asyncio.sleep(10)
    print(await ploudos.stop())

asyncio.run(main())

```
