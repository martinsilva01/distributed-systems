import socket, os

SOCK_PATH = "/tmp/print.sock"
try:
    os.remove(SOCK_PATH)
except FileNotFoundError:
    pass

server = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM)

server.bind(SOCK_PATH)

print(f"Server listening on {SOCK_PATH}...")
server.listen(1)

conn, _ = server.accept()
print("Connection accepted.")
try:
    while True:
        bytestring = conn.recv(256)
        if not bytestring:
            break
        string = bytestring.decode("utf-8")
        print(string)
    
finally:
    conn.close()
    server.close()

