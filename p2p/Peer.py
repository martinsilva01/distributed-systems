import time
import socket, os, threading, json, uuid, random

class Peer:

    def __init__(self, peer_id, role="default"):
        self.role = role
        self.peer_id = peer_id
        self.neighbor_set = set()
        self.seen_messages = set()
        self.sock_path = f"/tmp/peer_{peer_id}.sock"
        self.print_lock = threading.Lock()
    
        self.client_wait = False
        self.client_event = threading.Event()   # <-- REQUIRED

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


    def handle_connection(self, conn):
        try:
            data = conn.recv(4096).decode("utf-8")
            if not data:
                return
    
            msg = json.loads(data)
            sender = msg.get("sender")
            message_id = msg.get("message_id")
            payload = msg.get("payload")
            neighbors = msg.get("neighbors", [])
            success_flag = msg.get("success", False)
            client_id = msg.get("client_id", None)
    
            self.neighbor_set.update(neighbors)
    
            if message_id in self.seen_messages:
                return
            self.seen_messages.add(message_id)
    
            # Client receives success
            if self.role == "client" and success_flag and client_id == self.peer_id:
                self.client_event.set()
                return
    
            # Printer receives job
            if self.role == "printer" and payload:
                with self.print_lock:
                    print(f"[PRINTER {self.peer_id}] Received from {sender}")
                    print(payload)
                    print("PRINTING...")
                    time.sleep(5)
                    print("DONE")
    
                    self.success(sender)     # reply to client
                    return
    
            # Otherwise random walk
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
    
    #Send back to client by printer, job done.
    def success(self, client_id):
        msg = {
            "sender": self.peer_id,                 # PRINTER ID
            "message_id": str(uuid.uuid4()),
            "payload": "",                          # no payload needed
            "success": True,                        # boolean
            "client_id": client_id,
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

