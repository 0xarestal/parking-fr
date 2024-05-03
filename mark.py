import cv2
import pickle

width, height = 250, 190

try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []


def mouseClick(events, x, y, flags, params):
    global posList
    if events == cv2.EVENT_LBUTTONDOWN:
        alphabet = chr(ord('A') + len(posList))  # Assign the next alphabet
        posList.append((x, y, alphabet))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            if len(pos) == 3:  # Check if the tuple has three elements
                x1, y1, _ = pos
                if x1 < x < x1 + width and y1 < y < y1 + height:
                    posList.pop(i)

    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)


while True:
    img = cv2.imread("size.png")
    for pos in posList:
        if len(pos) == 3:  # Check if the tuple has three elements
            x, y, alphabet = pos
            cv2.rectangle(img, (x, y), (x + width, y + height), (255, 0, 255), 2)
            cv2.putText(img, alphabet, (x + 10, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('u'):
        alphabet = chr(ord('A') + len(posList))
        posList.append((100, 100, alphabet))  # Add a sample position for testing
        with open('CarParkPos', 'wb') as f:
            pickle.dump(posList, f)
    elif key == ord('i'):
        if posList:
            posList.pop()  # Remove the last position
            with open('CarParkPos', 'wb') as f:
                pickle.dump(posList, f)
    elif key == 27:  # 27 is the ASCII code for the Escape key
        break
