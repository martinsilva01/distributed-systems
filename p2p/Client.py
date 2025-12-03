
import time
import Receipt  # Your existing Receipt class
import random
import string
import uuid

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

        # pick a stable job id for this job
        job_id = str(uuid.uuid4())

        # METRICS
        peer.metrics["jobs_sent"] += 1
        peer.job_start_times[job_id] = time.time()

        # reset wait state
        peer.client_event.clear()

        # send job (include job_id)
        peer.broadcast_receipt(payload, job_id=job_id)
        print(f"[CLIENT {peer.peer_id}] Sent job {job_id}")

        # Wait for printer to reply (timeout to avoid hanging forever)
        if peer.client_event.wait(timeout=20):  # waits until Peer.handle_connection sets event
            print(f"[CLIENT {peer.peer_id}] Success for job {job_id}")
        else:
            peer.metrics["jobs_timed_out"] += 1
            print(f"[CLIENT {peer.peer_id}] Timeout waiting for job {job_id}")

        time.sleep(3)

