import asyncio
import httpx


class PloudOS:
    def __init__(self, username: str, password: str, server_id: int = 0, queue_timeout: int = 1500):
        """
        This is an unofficial API for PloudOS.
        It can be used to start, stop, queue and confirm servers.
        You can also retrieve info about your server.

        All of the functions in this class are fully asynchronous.

        Example use:
        ```py
        from ploudos import PloudOS

        ploudos = await PloudOS("myusername", "mypassword", 0)
        ```
        """
        self.username = username
        self.password = password
        self.server_id = server_id
        self.queue_timeout = queue_timeout
        self.client = httpx.AsyncClient(timeout=None)

    async def login(self):
        """
        This function logs you into PloudOS

        Returns None on success and an Exception on failure.

        Example use:
        ```py
        await ploudos.login()
        ```
        """
        data = {
            "username": self.username,
            "password": self.password
        }
        await self.client.post("https://ploudos.com/login/", data=data)

        if not self.client.cookies.get("PLOUDOS_SESSION_1"):
            raise Exception(f"Failed to login into PloudOS. Cookies in the session: {self.client.cookies}")
    

    async def get_server_info(self):
        """
        This function retrieves current server info.

        Returns a dictionary.

        Example use:
        ```py
        await get_server_info()
        ```
        """
        r = await self.client.get(f"https://ploudos.com/manage/{self.server_id}/ajax2")
        return r.json()
    

    async def queue(self):
        """
        This function executes the first step for starting the server from scratch.

        Returns a boolean.
        Returns `True` if the server needs confirmation (look at accept_server() function).
        Returns `False` if the server

        Example use:
        ```py
        await ploudos.queue()
        ```
        """
        r = await self.client.get(f"https://ploudos.com/manage/{self.server_id}/ajax2/queue/1")
        j = r.json()
        if j["error"]:
            raise Exception(f"Failed at queueing the server. Error: {j}")
        for i in range(self.queue_timeout):
            await asyncio.sleep(2)
            info = await self.get_server_info()
            if info["status"] == "WAITING_FOR_ACCEPT":
                return True
            elif info.get("isStarted") is True and info.get("isRunning") is True:
                # Server has already started. In this case, accepting is not necessary and this function can safely be cancelled.
                return False
        raise Exception("Queue function has timeouted")
    

    async def _start(self, r):
        j = r.json()
        if j["error"]:
            raise Exception(f"Failed at queueing the server. Error: {j}")
        while True:
            await asyncio.sleep(2)
            info = await self.get_server_info()
            if info.get("isStarted") is True and info.get("isRunning") is True:
                return info
    

    async def can_restart(self) -> bool:
        """
        This function checks if you can use restart() instead of queue() and accept_server().

        Returns a boolean.

        Example use:
        ```py
        await ploudos.can_restart()
        ```
        """
        info = await self.get_server_info()
        return info.get("isRunning") is False and info.get("isEditorMode") is False


    async def accept_server(self):
        """
        When starting the server from scratch, you have to accept server.
        You call this function after queue() returns True.
        If queue() returns False, this means the server has already started without accepting, so you don't have to call the function.

        Once this function ends, your server is now connectable and online.

        Returns None

        Example use:
        ```py
        await ploudos.accept_server()
        ```
        """
        r = await self.client.get(f"https://ploudos.com/manage/{self.server_id}/ajax2/accept")
        await self._start(r)
    

    async def restart(self):
        """
        This starts the server while it isn't yet fully stopped. This DOES NOT stop the server.

        Returns None

        Example use:
        ```py
        await ploudos.restart()
        ```
        """
        r = await self.client.get(f"https://ploudos.com/manage/{self.server_id}/ajax2/start")
        await self._start(r)


    async def stop(self):
        """
        This function stops your server.

        Returns a dictionary

        Example use:
        ```py
        await ploudos.stop()
        ```
        """
        r = await self.client.get(f"https://ploudos.com/manage/{self.server_id}/ajax2/stop")
        return r.json()


    async def exit_queue(self):
        """
        This function exits the queue.

        Returns a dictionary

        Example use:
        ```py
        await ploudos.exit_queue()
        ```
        """
        r = await self.client.get(f"https://ploudos.com/manage/{self.server_id}/ajax2/exitQueue")
        return r.json()
    

    async def close(self):
        """
        This function closes and releases resources used by this class.
        This should be called when you don't need to use this class anymore.
        Class WON'T WORK anymore, after you call this function.

        Returns None

        Example use:
        ```py
        await ploudos.close()
        ```
        """
        await self.client.aclose()
  

