from ultralytics import YOLO
import cv2

if __name__ == '__main__':
    # Load your trained model
    model = YOLO("C:/CrackSense/runs/cracksense_v1/weights/best.pt")

    # Run on a test image from the dataset
    import os
    test_images = os.listdir("C:/CrackSense/data/RDD_SPLIT/test/images")
    test_img = "C:/CrackSense/data/RDD_SPLIT/test/images/" + test_images[0]

    results = model(test_img, conf=0.25)
    results[0].show()  # opens a window with detections drawn

    # Print what was detected
    for box in results[0].boxes:
        cls = int(box.cls)
        conf = float(box.conf)
        names = ['longitudinal_crack', 'transverse_crack', 
                 'alligator_crack', 'pothole', 'other_damage']
        print(f"Detected: {names[cls]}  Confidence: {conf:.2f}")