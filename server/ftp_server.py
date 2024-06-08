# Created by Ryan Rueber and Christopher Qualls

import os
import asyncio
import socket

os.chdir('myfiles')

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100

EOF = "EOF"

serverPassword = "password"

intro_message = "Hello! Welcome to my quallsc and rueberr server! I'm majoring in CS\n"


async def client_handling(reader, writer):
    print("passwordStart\n")
    for attempts in range(3):
        passwordInput = "Enter Password"
        writer.write(passwordInput.encode())
        await writer.drain()

        data_length_hex = await reader.readexactly(8)
        # Then we convert it from hex to integer format that we can work with
        data_length = int(data_length_hex, 16)

        sent = await reader.read(data_length)
        password = sent.decode()
        print(password)
        print(attempts)
        if attempts >= 2 and password != serverPassword:
            writer.write(b"Too many attempts. Closing connection")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            break
        if password != serverPassword:
            writer.write(b"Incorrect \n")
            await writer.drain()
            print("incorrect \n")
        else:
            writer.write(intro_message.encode())
            await writer.drain()
            print("correct \n")
            break


    # command handling
    while True:

        data_length_hex = await reader.readexactly(8)
        # Then we convert it from hex to integer format that we can work with
        data_length = int(data_length_hex, 16)
        print("waiting for command")
        sent = await reader.read(data_length)
        print(sent.decode())
        if sent.decode() == "list":
            list = os.listdir(".")
            files = " ".join(list) + "\n"
            writer.write(files.encode())
            await writer.drain()
            print(files)
        elif sent.decode().startswith("put"):
            print(sent.decode()[4:])
            await putFunc(reader, writer, sent.decode()[4:])
        elif sent.decode().startswith("remove"):
            if os.path.exists(sent.decode()[7:]):
                os.remove(sent.decode()[7:])
                writer.write(b"ACK file removed")
                await writer.drain()
            else:
                writer.write(b"NAK file does not exist")
                await writer.drain()
        elif sent.decode().startswith("get"):
            if os.path.exists(sent.decode()[4:]):

                writer.write(b"ACK")
                await writer.drain()
                await getFunc(reader, writer, sent.decode()[4:])

            else:
                writer.write(b"NAK file does not exist")
                await writer.drain()
        elif sent.decode().startswith("close"):
            writer.close()
            await writer.wait_closed()
            break
        else:
            writer.write(b"NAK command does not exist")
            await writer.drain()

    return


async def putFunc(reader, writer, name):

    with open(name, 'wb') as f:
        while True:
            dataChunk = await reader.read(CHUNK)
            print(dataChunk)
            if not dataChunk or dataChunk.endswith(EOF.encode()):
                f.write(dataChunk[:-3])
                break
            f.write(dataChunk)
    f.close()
    writer.write(b"Uploaded file")
    await writer.drain()
    return


async def getFunc(reader, writer, name):
    with open(name, 'rb') as f:
        while dataChunk := f.read(CHUNK):
            writer.write(dataChunk)
            await writer.drain()
        writer.write(EOF.encode())
        await writer.drain()
    f.close()

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