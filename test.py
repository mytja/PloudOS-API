import asyncio
from ploudos import PloudOS

ploudos = PloudOS("myusername", "mypassword", 0)

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
        print(await ploudos.queue())
        print(await ploudos.accept_server())
    await asyncio.sleep(10)
    print(await ploudos.stop())

asyncio.run(main())
