# -*- coding: utf-8 -*-
import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("error in openning camera")
    exit()

cv2.namedWindow("video live", cv2.WINDOW_NORMAL)
cv2.resizeWindow("video live", 800, 600)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

overlay_image = cv2.imread(r"D:\horizon\deepseek.jpg") 

while True:
    ret, frame = cap.read()

    if not ret:
        print("fps reading error")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        resized_overlay = cv2.resize(overlay_image, (w, h))

        if resized_overlay.shape == frame[y:y+h, x:x+w].shape:
            frame[y:y+h, x:x+w] = resized_overlay

    cv2.imshow("video live", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()