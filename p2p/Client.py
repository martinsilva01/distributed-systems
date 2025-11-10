import time
import Receipt  # Your existing Receipt class

def run_client(peer):
    receipt = Receipt.Receipt(max_height=10, max_width=20)
    header = ["------DOORDASH------",
              "                    ",
              "      McDonalds     ",
              "--------------------"]
    body = ["McChicken      $1.99",
            "                    ",
            "    ORDER # 0001    ",
            "--------------------"]
    receipt.set_header(header)
    receipt.set_body(body)
    message = receipt.get_receipt()

    while True:
        payload = f"From Client {peer.peer_id}:\n{message}"
        peer.broadcast_receipt(payload)
        print(f"[CLIENT {peer.peer_id}] Sent receipt")
        time.sleep(3)

