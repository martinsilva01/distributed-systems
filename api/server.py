from flask import Flask, send_from_directory, jsonify, request, abort
import os

app = Flask(__name__)

IMAGE_DIR = os.path.join(os.getcwd(), "food")
restaurant_list = ["McDonalds", "Raising Canes", "Burger King", "Jack in the Box", "Carl's Jr.", "In-N-Out", "Wingstop", "Panda Express", "Chipotle", "Taco Bell", "KFC"]

@app.route('/food/<string:imageName>', methods = ['GET'])
def getFoodImage(imageName):
    if ".." in imageName or "/" in imageName or "\\" in imageName:
        abort(400, "Invalid name")

    if not os.path.exists(os.path.join(IMAGE_DIR, imageName + ".jpg")):
        abort(404, "Image not found")

    return send_from_directory(IMAGE_DIR, imageName + ".jpg")

@app.route('/restaurant', methods = ['GET'])
def getRestaurantList():
   return jsonify(restaurant_list) 


if __name__ == "__main__":
    app.run(debug=True)

