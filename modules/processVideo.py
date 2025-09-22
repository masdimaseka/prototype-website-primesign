import os
import tempfile
import subprocess
from collections import Counter, deque
from typing import Optional, Callable, Tuple, List

import cv2
import numpy as np
from ultralytics import YOLO

from .subtitles import SubtitleEvent, events_to_srt, draw_caption_bottom

ProgressFn = Optional[Callable[[int, int, str], None]]

def _make_writer(path: str, fps: float, size: tuple[int, int]) -> cv2.VideoWriter:
    w, h = size
    fourcc_mp4v = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc_mp4v, fps, (w, h))
    if writer.isOpened(): return writer
    
    fourcc_avc1 = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(path, fourcc_avc1, fps, (w, h))
    if writer.isOpened(): return writer
    
    raise RuntimeError("Gagal menginisialisasi VideoWriter. Pastikan OpenCV dan codec video (seperti ffmpeg) ter-install dengan benar.")

def _ffmpeg_transcode_to_h264(src_path: str) -> str | None:
    try:
        out_path = src_path.replace(".mp4", "_h264.mp4")
        cmd = [
            "ffmpeg",
            "-y",                   
            "-i", src_path,        
            "-c:v", "libx264",      
            "-pix_fmt", "yuv420p",  
            "-movflags", "+faststart", 
            "-c:a", "copy",         
            out_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            # print(f"Transcode berhasil: {os.path.basename(src_path)} -> {os.path.basename(out_path)}")
            return out_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Transcode gagal untuk {os.path.basename(src_path)}. Error: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            print(f"FFmpeg stderr: {e.stderr.decode()}")
        pass
    return None

def process_video(
    file_bytes: bytes,
    model_path: str,
    cfg: dict,  
    progress_cb: ProgressFn = None,
) -> Tuple[str, str, str]:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(file_bytes)
        input_path = tmp_in.name

    model = YOLO(model_path)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        try: os.remove(input_path)
        except Exception: pass
        raise RuntimeError("Gagal membuka video input.")

    orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    frame_skip = max(int(round(orig_fps / max(1, cfg['target_fps']))), 1)

    tmp_out_boxes = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4"); tmp_out_boxes.close()
    boxes_path_raw = tmp_out_boxes.name
    out_boxes = _make_writer(boxes_path_raw, orig_fps, (width, height))

    tmp_out_caption = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4"); tmp_out_caption.close()
    caption_path_raw = tmp_out_caption.name
    out_caption = _make_writer(caption_path_raw, orig_fps, (width, height))

    vote_window = deque(maxlen=cfg['window_vote'])
    stable_label: str = ""
    last_winner: str = ""
    winner_streak: int = 0

    events: List[SubtitleEvent] = []
    current_event: Optional[SubtitleEvent] = None

    last_boxes_frame: Optional[np.ndarray] = None
    last_caption_frame: Optional[np.ndarray] = None

    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if current_event is not None:
                    current_event.end_frame = frame_idx - 1
                    events.append(current_event)
                break

            process_this = (frame_idx % frame_skip == 0)
            
            if process_this:
                results = model.predict(frame, conf=cfg['conf'], iou=cfg['iou'], verbose=False)

                top_label = ""
                if results and results[0].boxes and len(results[0].boxes) > 0:
                    r = results[0]
                    max_i = int(np.argmax(r.boxes.conf.cpu().numpy()))
                    cls = int(r.boxes.cls[max_i].item())
                    top_label = r.names.get(cls, str(cls))
                    boxes_frame = r.plot()
                else:
                    boxes_frame = frame.copy()

                if top_label:
                    vote_window.append(top_label)
                    winner, win_count = Counter(vote_window).most_common(1)[0]
                    win_ratio = win_count / len(vote_window)

                    if winner == last_winner: winner_streak += 1
                    else: last_winner, winner_streak = winner, 1

                    if not stable_label:
                        if win_ratio >= cfg['start_threshold'] and winner_streak >= cfg['cons_frame']:
                            stable_label = winner
                            current_event = SubtitleEvent(start_frame=frame_idx, end_frame=None, text=stable_label)
                    else: 
                        if winner != stable_label:
                            if win_ratio >= cfg['start_threshold'] and winner_streak >= cfg['cons_frame']:
                                if current_event:
                                    current_event.end_frame = frame_idx - 1
                                    events.append(current_event)
                                stable_label = winner
                                current_event = SubtitleEvent(start_frame=frame_idx, end_frame=None, text=stable_label)
                        else: 
                            if win_ratio <= cfg['end_threshold'] and current_event:
                                current_event.end_frame = frame_idx - 1
                                events.append(current_event)
                                current_event, stable_label = None, ""
                
                caption_frame = draw_caption_bottom(frame.copy(), stable_label)
                last_boxes_frame = boxes_frame
                last_caption_frame = caption_frame

            canvas_boxes = last_boxes_frame if last_boxes_frame is not None else frame
            canvas_caption = last_caption_frame if last_caption_frame is not None else draw_caption_bottom(frame.copy(), stable_label)

            out_boxes.write(canvas_boxes)
            out_caption.write(canvas_caption)

            frame_idx += 1
            if progress_cb: progress_cb(frame_idx, total_frames, stable_label)

    finally:
        cap.release()
        out_boxes.release()
        out_caption.release()
        try: os.remove(input_path)
        except Exception: pass
    
    boxes_path = _ffmpeg_transcode_to_h264(boxes_path_raw) or boxes_path_raw
    caption_path = _ffmpeg_transcode_to_h264(caption_path_raw) or caption_path_raw

    if boxes_path != boxes_path_raw:
        try: os.remove(boxes_path_raw)
        except Exception as e: print(f"Warning: Gagal menghapus file sementara {boxes_path_raw}: {e}")
    if caption_path != caption_path_raw:
        try: os.remove(caption_path_raw)
        except Exception as e: print(f"Warning: Gagal menghapus file sementara {caption_path_raw}: {e}")
    
    srt_text = events_to_srt(events, fps=orig_fps)
    return boxes_path, caption_path, srt_text