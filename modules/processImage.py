import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import io

def process_image(
    image_bytes: bytes,
    model_path: str,
    conf: float,
) -> np.ndarray:
   
    model = YOLO(model_path)

    pil_image = Image.open(io.BytesIO(image_bytes))
    
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    results = model.predict(frame, conf=conf, verbose=False)
    result = results[0]
    result_plotted = result.plot()

    return result_plotted