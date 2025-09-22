import tempfile
from typing import Dict, Any, Tuple
import cv2

def read_video_info(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(file_bytes)
    tmp.flush()
    tmp_path = tmp.name
    tmp.close()

    cap = cv2.VideoCapture(tmp_path)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError("Tidak bisa membuka video yang diupload.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frames / fps if fps > 0 else 0.0

    cap.release()
    return tmp_path, {
        "fps": round(fps, 3),
        "width": width,
        "height": height,
        "frames": frames,
        "duration_s": round(duration, 3),
        "resolution": f"{width}x{height}",
    }
