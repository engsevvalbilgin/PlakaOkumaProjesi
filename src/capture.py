import cv2
webcam = cv2.VideoCapture(0)
stop=False
while stop==False:
    ret,frame=webcam.read()
    if ret==True:
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        cv2.imshow("GriFrame",gray)
        cv2.imshow('Şevval',frame)
        key=cv2.waitKey(1)
        if key==ord("q"):
            break
webcam.release()
cv2.destroyAllWindows()
