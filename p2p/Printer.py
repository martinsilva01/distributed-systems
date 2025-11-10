import time

def run_printer(peer):
    print(f"[PRINTER {peer.peer_id}] Ready to receive messages...")
    while True:
        peer.ping()  # Update neighbor set
        time.sleep(5)

