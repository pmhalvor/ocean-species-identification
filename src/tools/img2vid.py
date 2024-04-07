import cv2
import sys
import os


def convert(img_dir, output_name="output.mp4", img_prefix="", img_suffix=".jpg", fps=5):
    img_array = []
    print(f'Frame directory: {img_dir}/')
    for filename in sorted(os.listdir(img_dir)):
        if not filename.endswith(img_suffix):
            continue

        if not filename.startswith(img_prefix):
            continue

        # print(f"Processing {img_dir / filename}")
        # img = cv2.imread(str(img_dir / filename))
        print(f'Processing {filename}')
        img = cv2.imread(str(f"{img_dir}/{filename}"))

        cv2.imshow('image', img)

        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)

    if len(img_array) == 0:
        print(f"No images found in {img_dir}")
        print(os.listdir(img_dir))
        return
    
    out = cv2.VideoWriter(
        filename=str(output_name), 
        fourcc=cv2.VideoWriter_fourcc(*"MP4V"), 
        fps=int(fps), 
        frameSize=size
    )

    for i in range(len(img_array)):
        out.write(img_array[i])

    out.release()


if __name__ == "__main__":
    
    if len(sys.argv)>1:
        convert(*sys.argv[1:])
    else:
        print("Usage: python3 img2video.py <file_pattern> <output_name>")