import cv2
import sys
import os

# env var INPUT and OUTPUT_DIR are set in the Dockerfile
INPUT_DIR = os.environ.get("INPUT_DIR", ".")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")


def convert(img_dir, output_name="output.mp4", img_prefix="", img_suffix=".jpg", fps=5):
    img_array = []
    img_dir_full_path = os.path.join(INPUT_DIR, img_dir)
    print(f'Frame directory: {img_dir_full_path}/')
    for filename in sorted(os.listdir(img_dir_full_path)):
        if not filename.endswith(img_suffix):
            continue

        if not filename.startswith(img_prefix):
            continue

        print(f'Processing {filename}')
        img = cv2.imread(os.path.join(img_dir_full_path, filename))

        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)

    if len(img_array) == 0:
        print(f"No images found in {img_dir_full_path}")
        print(os.listdir(img_dir_full_path))
        return
    
    out = cv2.VideoWriter(
        filename=str(os.path.join(OUTPUT_DIR, output_name)), 
        fourcc=cv2.VideoWriter_fourcc(*"MP4V"), 
        fps=int(fps), 
        frameSize=size
    )

    for i in range(len(img_array)):
        out.write(img_array[i])

    out.release()


def vid2gif(video_path, gif_path):
    """Convert a video to a gif."""
    import moviepy.editor as mp  # TODO move to global scope

    clip = mp.VideoFileClip(video_path)
    clip.write_gif(gif_path)
    return gif_path


if __name__ == "__main__":
    
    if len(sys.argv)>1:
        convert(*sys.argv[1:])
    else:
        print("Usage: python3 img2video.py <image_dir> <output_name>")