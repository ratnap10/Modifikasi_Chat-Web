#!/usr/bin/env python3
import asyncio
import websockets

# Set untuk menyimpan semua client yang terhubung
connected_clients = {}

# Fungsi untuk menangani koneksi WebSocket
async def handler(websocket):
    try:
        # Terima username dari client baru
        username = await websocket.recv()
        connected_clients[websocket] = username  # Simpan username di dictionary

        # Kirim pesan pribadi ke client baru
        await websocket.send(f"Kamu bergabung ke CiChat atas nama {username}.")  # Pesan khusus untuk dirinya sendiri

        # Kirim notifikasi join ke semua client lain
        join_message = f"{username} telah bergabung ke CiChat."
        print(join_message)
        await broadcast(join_message, sender=websocket)  # Broadcast ke semua client kecuali pengirim

        # Tangani pesan dari client
        async for message in websocket:
            broadcast_message = f"{username}: {message}"
            print(broadcast_message)
            await broadcast(broadcast_message, sender=websocket)  # Broadcast pesan ke semua client
    except websockets.ConnectionClosed:
        pass
    finally:
        # Tangani client yang keluar
        if websocket in connected_clients:
            leave_message = f"{connected_clients[websocket]} telah keluar dari CiChat."
            print(leave_message)
            del connected_clients[websocket]  # Hapus client dari dictionary
            await broadcast(leave_message, sender=None)  # Broadcast notifikasi ke semua client

# Fungsi untuk mengirim pesan ke semua client (broadcast)
async def broadcast(message, sender=None):
    tasks = [
        client.send(message)
        for client in connected_clients
        if client != sender  # Jangan kirim pesan ke pengirim
    ]
    if tasks:  # Pastikan ada client untuk dikirim
        await asyncio.gather(*tasks)

# Fungsi utama untuk menjalankan server
async def main():
    print("WebSocket chat server with username listening on ws://localhost:6789")
    async with websockets.serve(handler, "localhost", 6789):
        await asyncio.Future()  # Menjaga server tetap berjalan

if __name__ == "__main__":
    asyncio.run(main())
