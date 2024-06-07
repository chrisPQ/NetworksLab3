import os
import asyncio
import socket
from threading import Thread

CHUNK = 100

EOF = "EOF"

IP, DPORT = 'localhost', 8080

os.chdir('myfiles')

def to_hex(number):
    # Verify our assumption: error is printed and program exists if assumption is violated
    assert number <= 0xffffffff, "Number too large"
    return "{:08x}".format(number)


async def recv_message(reader: asyncio.StreamReader):
    full_data = await reader.read(CHUNK)
    return full_data.decode()


async def connect(i):
    # Configure a socket object to use IPv4 and TCP
    reader, writer = await asyncio.open_connection(IP, DPORT)
    correctPassword = False
    # TODO: receive the introduction message by implementing `recv_intro_message` above.
    while not correctPassword:
        intro = await recv_message(reader)
        print(intro)

        # Get the filename to send from the user
        filename = input(" ")

        # Send the filename to the server
        await send_long_message(writer, filename)

        # Receive a response from the server
        intro = await recv_message(reader)
        if intro == "Incorrect \n":

            print(intro)
        else:
            print(intro)

            break

    while True:
        command = input("Command to send: ")

        if command.startswith("list"):
            await send_long_message(writer, command)
            data = await recv_message(reader)
            if not data:
                break
            print(data)
        elif command.startswith("put"):
            if os.path.exists(command[4:]):
                await send_long_message(writer, command)
                with open(command[4:], 'rb') as f:
                    while sendData := f.read(CHUNK):
                        writer.write(sendData)
                        await writer.drain()
                f.close()
                writer.write(EOF.encode())
                await writer.drain()
                print(await recv_message(reader))
            else:
                print("file does not exist")
        elif command.startswith("remove"):
            await send_long_message(writer, command)
            print(await recv_message(reader))
        elif command.startswith("get"):
            await send_long_message(writer, command)
            server_response = await recv_message(reader)
            if server_response.decode() == "ACK":
                print("file exists")
            elif server_response.decode() == "does not exist":
                print("file doesn't exist")
        elif command.startswith("close"):
            writer.close()
            await writer.wait_closed()




    # Read in the contents of the file



    """
    Part 2: Long Message Exchange Protocol
    """
    # TODO: Send message to the server by implementing `send_long_message` above.
    # await send_long_message(writer, long_msg)



async def send_long_message(writer: asyncio.StreamWriter, data):
    # TODO: Send the length of the message: this should be 8 total hexadecimal digits
    #       This means that ffffffff hex -> 4294967295 dec
    #       is the maximum message length that we can send with this method!
    #       hint: you may use the helper function `to_hex`. Don't forget to encode before sending!

    writer.write(to_hex(len(data)).encode())
    writer.write(data.encode())

    await writer.drain()



async def main(tosend):
    tasks = []
    for i in range(1):
        tasks.append(connect(tosend + str(i).rjust(8, '0')))
    # await connect(str(0).rjust(8, '0'))

    await asyncio.gather(*tasks)
    print("done")


# Run the `main()` function
if __name__ == "__main__":
    tosend = "whoops"

    asyncio.run(main(tosend))