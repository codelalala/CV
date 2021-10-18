from typing import no_type_check
import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
from collections import deque

#######################################
wCam, hCam = 1280, 720
marginTop = 150  # Frame Reduction
marginLR = 200
marginBottom = 150
smoothening = 12
draw = False
#######################################
pTime = 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

x_deq = deque()
y_deq = deque()
for _ in range(smoothening):
    x_deq.append(0)
    y_deq.append(0)

buttons_flag = [False, False, False]  # LEFT,RIGHT,MIDDLE
detect_flag = False

detector = htm.handDetector(maxHands=1, detectionCon=0.8, trackCon=0.8)
wScr, hScr = autopy.screen.size()


while True:
    # 1. Find hand landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox, img = detector.findPosition(img)

    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        if (
            fingers[0] == 1
            and fingers[1] == 1
            and fingers[2] == 1
            and fingers[3] == 1
            and fingers[4] == 1
        ):
            detect_flag = True
        if detect_flag == True:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            # start detection
            # print(fingers)
            # 4. Only Index Finger: Moving mode
            cv2.rectangle(
                img,
                (marginLR, marginTop),
                (wCam - marginLR, hCam - marginBottom),
                (255, 0, 255),
                2,
            )
            if fingers[1] == 1:
                # moving mode
                # 6. Smoothen Values
                x_deq.popleft()
                x_deq.append(x1)
                y_deq.popleft()
                y_deq.append(y1)
                x_smooth = sum(x_deq) / smoothening
                y_smooth = sum(y_deq) / smoothening
                # 5. Convert coordinates
                x3 = np.interp(x_smooth, (marginLR, wCam - marginLR), (1, wScr))
                y3 = np.interp(
                    y_smooth, (marginTop, hCam - marginBottom), (0, hScr - 1)
                )

                # 7. Move Mouse
                autopy.mouse.move(wScr - x3, y3)
                if draw:
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

                # if finger_sum > finger_thresh:
                if fingers[2] == 0 and fingers[3] == 0:
                    if fingers[0] == 1:
                        if buttons_flag[0] == True:
                            print("Left Button Released")
                            autopy.mouse.toggle(autopy.mouse.Button.LEFT, down=False)
                            buttons_flag[0] = False
                        if buttons_flag[1] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.RIGHT, down=False)
                            buttons_flag[1] = False
                        if buttons_flag[2] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.MIDDLE, down=False)
                            buttons_flag[2] = False
                    else:
                        if buttons_flag[0] == False:
                            print("Left Button Down")
                            autopy.mouse.toggle(autopy.mouse.Button.LEFT, down=True)
                            buttons_flag[0] = True
                        if buttons_flag[1] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.RIGHT, down=False)
                            buttons_flag[1] = False
                        if buttons_flag[2] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.MIDDLE, down=False)
                            buttons_flag[2] = False
                    if draw:
                        cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                elif fingers[2] == 1 and fingers[3] == 0:
                    if fingers[0] == 1:
                        if buttons_flag[0] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.LEFT, down=False)
                            buttons_flag[0] = False
                        if buttons_flag[1] == True:
                            print("Right Button Released")
                            autopy.mouse.toggle(autopy.mouse.Button.RIGHT, down=False)
                            buttons_flag[1] = False
                        if buttons_flag[2] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.MIDDLE, down=False)
                            buttons_flag[2] = False
                    else:
                        if buttons_flag[0] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.LEFT, down=False)
                            buttons_flag[0] = False
                        if buttons_flag[1] == False:
                            print("Right Button Down")
                            autopy.mouse.toggle(autopy.mouse.Button.RIGHT, down=True)
                            buttons_flag[1] = True
                        if buttons_flag[2] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.MIDDLE, down=False)
                            buttons_flag[2] = False
                elif fingers[2] == 1 and fingers[3] == 1:
                    if fingers[0] == 1:
                        if buttons_flag[0] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.LEFT, down=False)
                            buttons_flag[0] = False
                        if buttons_flag[1] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.RIGHT, down=False)
                            buttons_flag[1] = False
                        if buttons_flag[2] == True:
                            print("Middle Button Released")
                            autopy.mouse.toggle(autopy.mouse.Button.MIDDLE, down=False)
                            buttons_flag[2] = False
                    else:
                        if buttons_flag[0] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.LEFT, down=False)
                            buttons_flag[0] = False
                        if buttons_flag[1] == True:
                            autopy.mouse.toggle(autopy.mouse.Button.RIGHT, down=False)
                            buttons_flag[1] = False
                        if buttons_flag[2] == False:
                            print("Middle Button Down")
                            autopy.mouse.toggle(autopy.mouse.Button.MIDDLE, down=True)
                            buttons_flag[2] = True

    else:
        detect_flag = False
        if buttons_flag[0] == True:
            autopy.mouse.toggle(autopy.mouse.Button.LEFT, down=False)
            buttons_flag[0] = False
        if buttons_flag[1] == True:
            autopy.mouse.toggle(autopy.mouse.Button.RIGHT, down=False)
            buttons_flag[1] = False
        if buttons_flag[2] == True:
            autopy.mouse.toggle(autopy.mouse.Button.MIDDLE, down=False)
            buttons_flag[2] = False
    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    if draw:
        cv2.putText(
            img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3
        )
    # 12. Display
    if draw:
        cv2.imshow("Image", img)
    cv2.waitKey(1)
