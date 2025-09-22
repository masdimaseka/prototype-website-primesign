def get_preset(preset_name):
    config = {
        "conf": 0.70,
        "iou": 0.50,
        "target_fps": 15,
        "window_vote": 5,
        "cons_frame": 5,
        "start_threshold": 0.70,
        "end_threshold": 0.50
    }

    if preset_name == "Cepat":
        config = {
            "conf": 0.50,
            "iou": 0.30,
            "target_fps": 10,
            "window_vote": 3,
            "cons_frame": 3,
            "start_threshold": 0.50,
            "end_threshold": 0.30
        }
    elif preset_name == "Akurat":
        config = {
            "conf": 0.90,
            "iou": 0.70,
            "target_fps": 30,
            "window_vote": 7,
            "cons_frame": 7,
            "start_threshold": 0.90,
            "end_threshold": 0.70
        }
        
    return config

def override_config(base_config, **overrides):
    final_config = base_config.copy()  
    final_config.update(overrides)     
    return final_config
    
