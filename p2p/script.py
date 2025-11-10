from Peer import Peer
import Client, Printer
import threading, time, os

NUM_CLIENTS = 5
NUM_PRINTERS = 5
all_peers = []

# Create clients
peer_id = 0
for _ in range(NUM_CLIENTS):
    all_peers.append(Peer(peer_id, role="client"))
    peer_id += 1

# Create printers
for _ in range(NUM_PRINTERS):
    all_peers.append(Peer(peer_id, role="printer"))
    peer_id += 1

time.sleep(1)  # Allow sockets to bind

# Assign neighbors (fully connected network for simplicity)
for peer in all_peers:
    for neighbor in all_peers:
        if neighbor.sock_path != peer.sock_path:
            peer.neighbor_set.add(neighbor.sock_path)

# Launch clients
for peer in all_peers:
    if peer.role == "client":
        threading.Thread(target=Client.run_client, args=(peer,), daemon=True).start()
    elif peer.role == "printer":
        threading.Thread(target=Printer.run_printer, args=(peer,), daemon=True).start()

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down peers...")
    for peer in all_peers:
        peer.server.close()
        if os.path.exists(peer.sock_path):
            os.unlink(peer.sock_path)

