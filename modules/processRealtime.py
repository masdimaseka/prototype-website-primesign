import cv2
from ultralytics import YOLO

def process_frame(model_path: str, frame, confidence: float):

    model = YOLO(model_path)
    
    results = model.predict(frame, conf=confidence, verbose=False)
    
    detected_classes = set()
    class_names = results[0].names
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = class_names[class_id]
        detected_classes.add(class_name)
    
    annotated_frame = results[0].plot()
    
    annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    
    return annotated_frame_rgb, detected_classes