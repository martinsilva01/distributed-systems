
import time
import socket, os, threading, json, uuid, random

class Peer:

    def __init__(self, peer_id, role="default"):
        self.role = role
        self.peer_id = peer_id
        self.neighbor_set = set()     # contains neighbor socket paths
        self.seen_messages = set()
        self.sock_path = f"/tmp/peer_{peer_id}.sock"

        # local lock to serialize the actual print operation on this process
        self.print_lock = threading.Lock()

        # client waiting event (client waits for printer success reply)
        self.client_event = threading.Event()

        # ===== Ricart-Agrawala (RA) state =====
        self.clock = 0                    # lamport logical clock
        self.requesting_cs = False        # are we requesting CS?
        self.request_ts = None            # timestamp of our request
        self.replies_needed = set()       # set of neighbor paths we still need REPLY from
        self.deferred_replies = set()     # neighbor paths to reply to when we exit CS
        self.ra_cs_event = threading.Event()  # event to wait for RA replies
        self.ra_timeout = 10              # seconds to wait for RA replies before timeout
        # ======================================

        # Remove old socket if exists
        if os.path.exists(self.sock_path):
            os.unlink(self.sock_path)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.sock_path)
        self.server.listen(10)

        # Start listener thread
        threading.Thread(target=self.listen_loop, daemon=True).start()

    # -------------------------
    # Lamport helpers
    # -------------------------
    def incr_clock(self, remote_ts=None):
        """Increment Lamport clock; if remote_ts supplied, sync to it."""
        if remote_ts is None:
            self.clock += 1
        else:
            # take max(remote, local) + 1
            self.clock = max(self.clock, remote_ts) + 1
        return self.clock

    # -------------------------
    # Networking helpers
    # -------------------------
    def send(self, path, msg):
        """Send JSON msg to a specific unix socket path. Returns True/False."""
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(path)
            s.send(json.dumps(msg).encode("utf-8"))
            s.close()
            return True
        except Exception:
            return False

    def random_walk(self, msg):
        """Forward receipt-like messages along a single random neighbor."""
        choices = list(self.neighbor_set - {self.sock_path})
        if not choices:
            return
        nxt = random.choice(choices)
        self.send(nxt, msg)

    # -------------------------
    # Ricart-Agrawala: request CS
    # -------------------------
    def request_cs(self, timeout=None):
        """
        Request distributed critical section using Ricart-Agrawala.
        Blocks until all REPLY messages are received or timeout expires.
        Returns True if entered CS, False on timeout.
        """
        timeout = self.ra_timeout if timeout is None else timeout

        # increment local lamport clock and record request timestamp
        self.incr_clock()
        self.request_ts = self.clock
        self.requesting_cs = True

        # replies_needed are direct neighbor socket paths (expect REPLY from each)
        self.replies_needed = set(self.neighbor_set - {self.sock_path})
        self.deferred_replies.clear()
        self.ra_cs_event.clear()

        # build REQ message (include sender_path so recipients can reply directly)
        req_msg = {
            "type": "REQ",
            "sender_id": self.peer_id,
            "sender_path": self.sock_path,
            "ts": self.request_ts
        }

        # send REQ directly to all neighbors (not random walk)
        for neighbor_path in list(self.replies_needed):
            self.send(neighbor_path, req_msg)

        # if there are no neighbors, immediately allow entry
        if not self.replies_needed:
            self.ra_cs_event.set()
            return True

        # wait for replies or timeout
        got = self.ra_cs_event.wait(timeout=timeout)
        if not got:
            # timeout: clean up RA state and return False
            self.requesting_cs = False
            self.request_ts = None
            # we intentionally keep deferred_replies as-is; callers can retry later
            return False

        return True

    def release_cs(self):
        """Release CS and send any deferred replies."""
        self.requesting_cs = False
        self.request_ts = None

        # Send REPLY to any deferred requesters
        for p in list(self.deferred_replies):
            rep = {
                "type": "REPLY",
                "sender_id": self.peer_id,
                "sender_path": self.sock_path
            }
            self.send(p, rep)
        self.deferred_replies.clear()

    # -------------------------
    # Listener / message handling
    # -------------------------
    def listen_loop(self):
        while True:
            conn, _ = self.server.accept()
            threading.Thread(target=self.handle_connection, args=(conn,), daemon=True).start()

    def handle_connection(self, conn):
        try:
            data = conn.recv(65536).decode("utf-8")
            if not data:
                return

            # parse message
            msg = json.loads(data)

            # ---- RA messages first ----
            if msg.get("type") == "REQ":
                self.handle_req(msg)
                return
            if msg.get("type") == "REPLY":
                self.handle_reply(msg)
                return

            # ---- other messages (receipts, success replies, etc.) ----
            sender = msg.get("sender")
            message_id = msg.get("message_id")
            payload = msg.get("payload")
            neighbors = msg.get("neighbors", [])
            success_flag = msg.get("success", False)
            client_id = msg.get("client_id", None)

            # update neighbor set using any neighbor info included in the message
            self.neighbor_set.update(neighbors)

            # deduplicate
            if message_id in self.seen_messages:
                return
            self.seen_messages.add(message_id)

            # Client receives success reply from printer
            if self.role == "client" and success_flag and client_id == self.peer_id:
                # signal client waiting loop
                self.client_event.set()
                return

            # Printer receives a print job (payload)
            if self.role == "printer" and payload:
                # Use RA to acquire global printing permission
                acquired = self.request_cs(timeout=self.ra_timeout)
                if not acquired:
                    print(f"[PRINTER {self.peer_id}] RA timeout acquiring CS — aborting job from {sender}")
                    return

                # Local guard as well so only one print happens concurrently in-process
                with self.print_lock:
                    print(f"[PRINTER {self.peer_id}] Entered CS and printing job from {sender}")
                    print("PRINTING...")
                    time.sleep(5)
                    print(payload)
                    print(f"[PRINTER {self.peer_id}] DONE")

                # After leaving CS send deferred replies and notify client
                self.release_cs()
                self.success(sender)
                return

            # otherwise forward using random-walk as before
            self.random_walk(msg)

        finally:
            conn.close()

    # -------------------------
    # RA handlers
    # -------------------------
    def handle_req(self, msg):
        """
        Incoming REQ fields: type='REQ', sender_id, sender_path, ts
        """
        sender_path = msg.get("sender_path")
        sender_id = msg.get("sender_id")
        ts = msg.get("ts", 0)

        # update lamport clock relative to incoming ts
        self.incr_clock(remote_ts=ts)

        # if we're not requesting CS, reply immediately
        if not self.requesting_cs:
            rep = {"type": "REPLY", "sender_id": self.peer_id, "sender_path": self.sock_path}
            self.send(sender_path, rep)
            return

        # compare (ts, sender_id) lexicographically
        my_tuple = (self.request_ts, self.peer_id)
        their_tuple = (ts, sender_id)

        if their_tuple < my_tuple:
            # incoming request has priority -> reply immediately
            rep = {"type": "REPLY", "sender_id": self.peer_id, "sender_path": self.sock_path}
            self.send(sender_path, rep)
        else:
            # defer reply until after we exit CS
            self.deferred_replies.add(sender_path)

    def handle_reply(self, msg):
        """
        Incoming REPLY fields: type='REPLY', sender_id, sender_path
        """
        sender_path = msg.get("sender_path")
        # best-effort advance clock
        self.incr_clock()

        # remove this sender from replies_needed
        if sender_path in self.replies_needed:
            self.replies_needed.discard(sender_path)

        # if no more outstanding replies, set event to allow entry
        if not self.replies_needed:
            self.ra_cs_event.set()

    # -------------------------
    # Existing higher-level helpers
    # -------------------------
    def broadcast_receipt(self, text):
        """Client uses this to start a random-walk broadcast for a receipt."""
        msg = {
            "sender": self.peer_id,
            "message_id": str(uuid.uuid4()),
            "payload": text,
            "neighbors": list(self.neighbor_set | {self.sock_path})
        }
        # start random walk
        self.random_walk(msg)

    def success(self, client_id):
        """Send a success notification back towards the client (random-walk)."""
        msg = {
            "sender": self.peer_id,                 # PRINTER ID
            "message_id": str(uuid.uuid4()),
            "payload": "",                          # no payload needed
            "success": True,                        # boolean
            "client_id": client_id,
            "neighbors": list(self.neighbor_set | {self.sock_path})
        }
        self.random_walk(msg)

    def ping(self):
        """Ping neighbors to detect alive peers (keeps neighbor_set fresh)."""
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

