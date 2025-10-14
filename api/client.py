from PIL import Image
import requests
from io import BytesIO

BASE_URL = 'http://localhost:5000'

print(f"sending GET request to {BASE_URL}/restaurant")
r = requests.get(BASE_URL + '/restaurant')
if r.status_code == 200:
    print(r.json())

print(f"sending GET request to {BASE_URL}/food/cheeseburger")
r = requests.get(BASE_URL + '/food/cheeseburger')
if r.status_code == 200:
    image = Image.open(BytesIO(r.content))
    image.show()
else:
    print("Failed to fetch image")
