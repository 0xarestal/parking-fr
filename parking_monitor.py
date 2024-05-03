from flask import Flask, render_template, jsonify
from threading import Thread
import cv2
import pickle
import numpy as np

app = Flask(__name__)

url = 'http://192.168.0.107:8080/video'
cap = cv2.VideoCapture(0)

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 290, 180
prev_free_spots = 0

def checkParkingSpace(imgPro):
    spaceCounter = 0
    occupiedSlots = []

    for i, pos in enumerate(posList):
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            spaceCounter += 1
        else:
            occupiedSlots.append(chr(ord("A") + i))

    emptySlots = [chr(ord("A") + i) for i in range(len(posList)) if chr(ord("A") + i) not in occupiedSlots]

    return spaceCounter, emptySlots

def capture_video():
    global prev_free_spots
    while True:
        success, img = cap.read()
        if not success:
            print("Error capturing video frame.")
            break

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        free_spots, empty_spots = checkParkingSpace(imgDilate)


        cv2.putText(img, f'Free Spots: {free_spots}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f'Empty Spots: {", ".join(empty_spots)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        for i, pos in enumerate(posList):
            x, y = pos
            color = (0, 255, 0) if chr(ord("A") + i) in empty_spots else (0, 0, 255)
            thickness = 5 if chr(ord("A") + i) in empty_spots else 2
            cv2.rectangle(img, pos, (x + width, y + height), color, thickness)

        cv2.imshow("Parking Detection", img)

        if free_spots != prev_free_spots:
            print(f'Free Spots: {free_spots}, Empty Spots: {", ".join(empty_spots)}')

            with open('parking_info.txt', 'a') as file:
                file.write(f'Free Spots: {free_spots}, Empty Spots: {", ".join(empty_spots)}\n')

        prev_free_spots = free_spots

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
@app.route('/prototype')
def home():
    return render_template('prototype.html')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_overall_status')
def get_overall_status():
    return jsonify({'free': prev_free_spots, 'total': len(posList)})

if __name__ == '__main__':
    video_thread = Thread(target=capture_video)
    video_thread.start()
    app.run(debug=True)
