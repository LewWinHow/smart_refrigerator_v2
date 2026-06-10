import cv2
import requests
import time

DJANGO_URL = "http://127.0.0.1:8100/item/receive_and_detect_image/"

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

FRAME_INTERVAL = 0.2

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read camera frame")
            break

        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        try:
            files = {'image': ('frame.jpg', img_bytes, 'image/jpeg')}
            data = {'connect': '1'}
            response = requests.post(DJANGO_URL, files=files, data=data)
            print(f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print("Send failed:", e)
        time.sleep(FRAME_INTERVAL)

except KeyboardInterrupt:
    # Notify disconnection
    try:
        response = requests.post(DJANGO_URL, data={'connect': '0'})
        print("Interrupt send successful")
    except Exception as e:
        print("Disconnection failed:", e)
finally:
    cap.release()
