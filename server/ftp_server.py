import os
import asyncio
import socket

os.chdir('myfiles')

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100

serverPassword = "password"

intro_message = "Hello! Welcome to my (lyakhovs) server! I'm majoring in CS\n"


async def client_handling(reader, writer):

    for attempts in range(3):
        writer.write(b"Enter Password")
        await writer.drain()

        sent = await reader.read(CHUNK)
        password = sent.decode().strip()
        if password != serverPassword:
            writer.write(b"Incorrect \n")
            await writer.drain()
        else:
            writer.write(intro_message)
            await writer.drain()
            break
        if attempts >= 3:
            writer.write(b"Too many attempts. Closing connection")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            break

    return


async def main():
    server = await asyncio.start_server(
            client_handling,
            INTERFACE, SPORT
    )

    async with server:
        await server.serve_forever()

# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())