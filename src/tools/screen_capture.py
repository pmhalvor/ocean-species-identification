import numpy as np
import cv2
from mss import mss
from PIL import Image
import time 
import pickle as pkl
import os  
from pathlib import Path

from img2vid import convert

# can be used to capture specific area of screen, just replace monitor var
bounding_box = {'top': 100, 'left': 800, 'width': 800, 'height': 750}

# frame per second
FPS = 4 
FRAME_COUNT = 50

# prep for save 
save_dir = Path("data") / "video"
capture_name = "aquarium"

capture_number = len([f for f in os.listdir(save_dir) if f.startswith(capture_name)])
output_dir = (save_dir / f"{capture_name}_{capture_number:03d}")

os.makedirs(output_dir, exist_ok=True)


# capture loop
frames = []

with mss() as sct:
    monitor = sct.monitors[-1]  # bounding_box  

    for i in range(FRAME_COUNT):
        sct_img = sct.grab(monitor)

        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb, 'raw')
        arr = np.array(img)
        frames.append(arr)

        # cv2 swaps these for some reason? 
        if len(sct.monitors) > 2:
            cv2.imshow(capture_name, cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break

        time.sleep(1.0/FPS) # 1/FPS = seconds per frame

        print(f'Frame {i} captured ', arr.shape)

cv2.destroyAllWindows()

# save frames as images

imgs = [Image.fromarray(frame) for frame in frames]

os.makedirs(output_dir, exist_ok=True)
for j, img in enumerate(imgs):
    img.save(output_dir / f"frame_{j:03d}.jpg", )

print("capture saved at ", output_dir)

# convert to video
convert(output_dir, output_dir / f"{capture_name}_{capture_number:03d}.mp4", img_prefix="frame_", img_suffix=".jpg", fps=FPS)
