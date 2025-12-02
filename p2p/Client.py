import time
import Receipt  # Your existing Receipt class
import random
import string

def run_client(peer):
    receipt = Receipt.Receipt(max_height=10, max_width=20)
    header = ["------DOORDASH------",
              "                    ",
              "      McDonalds     ",
              "--------------------"]
    body = ["McChicken $1.99",
            "                    ",
            "    ORDER # 0001    ",
            "--------------------"]

    receipt.set_header(header)
    receipt.set_body(body)
    message = receipt.get_receipt()

    while True:
        random_string = "".join(random.choices(string.ascii_letters, k=20))
        payload = f"From Client {peer.peer_id}:\n{message}\n{random_string}\n"

        # Reset wait state
        peer.client_event.clear()

        peer.broadcast_receipt(payload)
        print(f"[CLIENT {peer.peer_id}] Sent receipt")

        # Wait for printer to reply
        if peer.client_event.wait(timeout=20): # <--- THIS BLOCKS UNTIL success()
            print(f"Success for client {peer.peer_id} print job")
        else:
            print(f"Client {peer.peer_id} timeout...")

        time.sleep(3)

