from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO("yolov8s.pt")

    model.train(
        data="C:/CrackSense/dataset.yaml",
        epochs=50,
        imgsz=640,
        batch=8,
        device=0,
        workers=0,
        project="C:/CrackSense/runs",
        name="cracksense_v1",
        patience=10,
        exist_ok=True
    )

    print("Training complete!")