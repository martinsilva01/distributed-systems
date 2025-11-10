
import socket, os, threading, json, uuid, random

class Peer:
    def __init__(self, peer_id, role="default"):
        self.role = role
        self.peer_id = peer_id
        self.neighbor_set = set()
        self.seen_messages = set()
        self.sock_path = f"/tmp/peer_{peer_id}.sock"

        # Remove old socket if exists
        if os.path.exists(self.sock_path):
            os.unlink(self.sock_path)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.sock_path)
        self.server.listen(10)

        # Start listener thread
        threading.Thread(target=self.listen_loop, daemon=True).start()

    # Listen for incoming connections
    def listen_loop(self):
        while True:
            conn, _ = self.server.accept()
            threading.Thread(target=self.handle_connection, args=(conn,), daemon=True).start()

    # Handle an incoming message
    def handle_connection(self, conn):
        try:
            data = conn.recv(4096).decode("utf-8")
            if not data:
                return
            msg = json.loads(data)
            sender = msg["sender"]
            message_id = msg["message_id"]
            payload = msg["payload"]
            neighbors = msg["neighbors"]

            self.neighbor_set.update(neighbors)

            # Skip already seen messages
            if message_id in self.seen_messages:
                return
            self.seen_messages.add(message_id)

            # Printers print once
            if self.role == "printer" and payload:
                print(f"[PRINTER {self.peer_id}] Received from {sender}")
                print(payload)
                print("-" * 30)
                return

            # Forward message to a random neighbor
            self.random_walk(msg)
        finally:
            conn.close()

    # Send a message to a specific peer path
    def send(self, path, msg):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(path)
            s.send(json.dumps(msg).encode("utf-8"))
            s.close()
            return True
        except:
            return False

    # Forward message to a random neighbor
    def random_walk(self, msg):
        choices = list(self.neighbor_set - {self.sock_path})
        if not choices:
            return
        nxt = random.choice(choices)
        self.send(nxt, msg)

    # Broadcast message (used by client)
    def broadcast_receipt(self, text):
        msg = {
            "sender": self.peer_id,
            "message_id": str(uuid.uuid4()),
            "payload": text,
            "neighbors": list(self.neighbor_set | {self.sock_path})
        }
        self.random_walk(msg)

    # Ping neighbors to remove dead ones
    def ping(self):
        alive = set()
        for n in list(self.neighbor_set):
            try:
                ok = self.send(n, {
                    "sender": self.peer_id,
                    "message_id": str(uuid.uuid4()),
                    "payload": "",
                    "neighbors": list(self.neighbor_set | {self.sock_path})
                })
                if ok:
                    alive.add(n)
            except:
                continue
        self.neighbor_set = alive

