import gradio as gr
import os
import shutil

from img2vid import convert as img2vid_convert

# img2vid related
INPUT_DIR = os.environ.get("INPUT_DIR", ".")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "output.mp4")

# gradio related
SERVER_NAME = os.environ.get("SERVER_NAME", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "7861"))


def prep_dirs():
    # create dir and remove any files currently here
    img_dir = os.path.join(INPUT_DIR, "images")
    os.makedirs(img_dir, exist_ok=True)
    for file in os.listdir(img_dir):
        os.remove(os.path.join(img_dir, file))

    os.makedirs(OUTPUT_DIR, exist_ok=True)   
    
    return img_dir, OUTPUT_PATH


def copy_files(files, dest_dir):
    for file in files:
        shutil.copy(file, dest_dir)
    

def img2vid_interface(files):
    img_dir, output_path = prep_dirs()
    copy_files(files, img_dir)

    # Convert images to video
    img2vid_convert(img_dir, output_path)

    return [
        gr.Video(label="Video", value=output_path),
        gr.DownloadButton(label="Download Video", value=output_path)
    ]


interface = gr.Interface(
    fn=img2vid_interface,
    inputs=gr.Files(label="Images", file_count="multiple"),
    outputs=[
        "video",
        gr.DownloadButton(),
    ],
    title="Image to Video Converter",
    description="Upload a series of images to create a video."
)


if __name__ == "__main__":
    interface.launch(server_name=SERVER_NAME, server_port=SERVER_PORT)