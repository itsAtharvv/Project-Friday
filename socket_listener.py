import asyncio
import os

async def socket_listener(trigger_callback):
    sock_path = "/tmp/friday.sock"
    if os.path.exists(sock_path):
        try:
            os.remove(sock_path)
        except OSError:
            pass
            
    async def handle_client(reader, writer):
        # We don't really care what they write, just that a connection/write happened
        data = await reader.read(100)
        writer.close()
        await writer.wait_closed()
        trigger_callback()

    server = await asyncio.start_unix_server(
        handle_client, sock_path
    )
    print(f"[Socket] Listening on {sock_path}")
    async with server:
        await server.serve_forever()
