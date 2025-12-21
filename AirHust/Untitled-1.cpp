import os
import shutil
import random

def copy_images_and_labels(src_path, dst_path):
    os.makedirs(f'../{dst_path}/images', exist_ok=True)
    os.makedirs(f'../{dst_path}/labels', exist_ok=True)

    for dir in ['train', 'val']:
        os.makedirs(f'../{dst_path}/images/' + dir, exist_ok=True)
        os.makedirs(f'../{dst_path}/labels/' + dir, exist_ok=True)
    
    for image_id in image_ids:
        shutil.copy(f"../{src_path}/images/{image_id}.jpg",
                    f"../{dst_path}/images/train/{image_id}.jpg")
        shutil.copy(f"../{src_path}/labels/{image_id}.txt",
                    f"../{dst_path}/labels/train/{image_id}.txt")
    
    for image_id in val_ids:
        shutil.copy(f"../{src_path}/images/{image_id}.jpg",
                    f"../{dst_path}/images/val/{image_id}.jpg")
        shutil.copy(f"../{src_path}/labels/{image_id}.txt",
                    f"../{dst_path}/labels/val/{image_id}.txt")

src_path = "dataset_all"
dst_path = "dataset6"
image_ids = [os.path.splitext(f)[0] for f in os.listdir(f'../{src_path}/labels') if
                f.endswith('.txt')]

# Shuffle the image ids and split into train and val
random.shuffle(image_ids)
split = int(0.1 * len(image_ids))
val_ids = image_ids[:split]
train_ids = image_ids[split:]
copy_images_and_labels(src_path, dst_path)