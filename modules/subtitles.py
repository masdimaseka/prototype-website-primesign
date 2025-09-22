from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np

@dataclass
class SubtitleEvent:
    start_frame: int
    end_frame: Optional[int] 
    text: str

def _fmt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def events_to_srt(events: List[SubtitleEvent], fps: float) -> str:
    lines = []
    idx = 1
    for ev in events:
        if ev.end_frame is None or ev.end_frame < ev.start_frame:
            continue
        start_s = ev.start_frame / max(1e-6, fps)
        end_s = ev.end_frame / max(1e-6, fps)
        lines.append(str(idx))
        lines.append(f"{_fmt_ts(start_s)} --> {_fmt_ts(end_s)}")
        lines.append(ev.text or "")
        lines.append("")  
        idx += 1
    return "\n".join(lines)

def draw_caption_bottom(img: np.ndarray, text: str) -> np.ndarray:
    if not text:
        return img
    out = img.copy()
    h, w = out.shape[:2]
    
    pad = 20
    font = cv2.FONT_HERSHEY_DUPLEX
    scale = 1.8 
    thickness = 3  

    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    box_w = tw + pad * 2
    box_h = th + baseline + pad
    x = (w - box_w) // 2
    y = h - box_h - 30 

    overlay = out.copy()
    cv2.rectangle(overlay, (x, y), (x + box_w, y + box_h), (0, 0, 0), -1)
    
    alpha = 0.6 
    cv2.addWeighted(overlay, alpha, out, 1 - alpha, 0, out)

    tx = x + pad
    ty = y + pad + th
    cv2.putText(out, text, (tx, ty), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
    return out