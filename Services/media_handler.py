import cv2

def process_video(file_path):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise Exception("Error opening video file.")
    return cap
