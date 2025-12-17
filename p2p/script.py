from Peer import Peer
import Client, Printer
import threading, time, os, signal, sys
import socketio

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
        print(f"peer {peer.peer_id}|  neighbor {neighbor.peer_id}")
        if abs(peer.peer_id - neighbor.peer_id) < 3 and peer.peer_id != neighbor.peer_id: 
            peer.neighbor_set.add(neighbor.sock_path)
            print("sending event")
            parsed_neighbor_list = []
            for path in peer.neighbor_set:
                neighbor_id = path.split("_")[-1].split(".")[0]
                parsed_neighbor_list.append(neighbor_id)
            Peer.sio.emit('edge_update', {
                "peer_id": peer.peer_id,
                "neighbor_set": parsed_neighbor_list
            })

# Launch clients and printers
for peer in all_peers:
    if peer.role == "client":
        threading.Thread(target=Client.run_client, args=(peer,), daemon=True).start()
    elif peer.role == "printer":
        threading.Thread(target=Printer.run_printer, args=(peer,), daemon=True).start()

def print_metrics_and_exit(signum=None, frame=None):
    print("\n===== SYSTEM METRICS =====")
    # aggregate client metrics
    total_sent = 0
    total_succeeded = 0
    total_timedout = 0
    total_violations = 0
    latencies_all = []
    for p in all_peers:
        if p.role == "client":
            m = p.metrics
            total_sent += m["jobs_sent"]
            total_succeeded += m["jobs_succeeded"]
            total_timedout += m["jobs_timed_out"]
            latencies_all += m["latencies"]
    # aggregate printer violations
    for p in all_peers:
        if p.role == "printer":
            total_violations += p.metrics["consistency_violations"]

    print(f"Total jobs sent: {total_sent}")
    print(f"Total succeeded: {total_succeeded}")
    print(f"Total timed out: {total_timedout}")
    if latencies_all:
        print(f"Avg latency: {sum(latencies_all)/len(latencies_all):.3f}s")
        print(f"Min latency: {min(latencies_all):.3f}s")
        print(f"Max latency: {max(latencies_all):.3f}s")
    else:
        print("No latency data collected.")
    print(f"Total consistency violations (duplicate prints): {total_violations}")

    # shutdown sockets cleanly
    for peer in all_peers:
        try:
            peer.server.close()
        except:
            pass
        if os.path.exists(peer.sock_path):
            try:
                os.unlink(peer.sock_path)
            except:
                pass
    sys.exit(0)

# hook Ctrl-C to print metrics
signal.signal(signal.SIGINT, print_metrics_and_exit)

# keep main thread alive
while True:
    time.sleep(1)

