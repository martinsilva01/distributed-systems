import socket, os
import Receipt
import time

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

SOCK_PATH = "/tmp/print.sock"
client = socket.socket(socket.AF_UNIX,
             socket.SOCK_STREAM)
client.connect(SOCK_PATH)
while True:
    client.sendall(message.encode('utf-8'))
    time.sleep(1)
