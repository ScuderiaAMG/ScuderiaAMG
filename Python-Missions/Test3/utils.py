import json
import os

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_coverage(field, drone):
    # 计算喷洒覆盖率
    total_crops = len(field.crops)
    if total_crops == 0:
        return 0
    
    sprayed_crops = 0
    for crop in field.crops:
        for x, y, radius in drone.sprayed_areas:
            dx = crop['x'] - x
            dy = crop['y'] - y
            distance = (dx*dx + dy*dy) ** 0.5
            if distance <= radius:
                crop['sprayed'] = True
                sprayed_crops += 1
                break
    
    return sprayed_crops / total_crops