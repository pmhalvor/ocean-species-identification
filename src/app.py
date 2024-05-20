import gradio as gr
import os

from super_resolution import YOLOv5ModelWithUpsample

# gradio-docker related
SERVER_NAME = os.environ.get("SERVER_NAME", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "7861"))


# tools
def save_outputs(output):
    default_output_path = os.path.join(
        os.getcwd(),
        "runs/detect/exp/"
    )

    if os.path.exists(default_output_path):
        print("Removing existing output images...")
        for f in os.listdir(default_output_path):
            os.remove(default_output_path + f)
        os.removedirs(default_output_path)

    print("Saving output images to", default_output_path)
    output.save()

    # TODO clean up
    return [
        os.path.join(default_output_path, f)
        for f in os.listdir(default_output_path)
    ]
    

# interface
def main(
        files,
        super_resolution=None,
        task="object_detection",
    ):

    if task == "object_detection":
        model = YOLOv5ModelWithUpsample(
            detection_model_path="../models/fathomnet_benthic/mbari-mb-benthic-33k.pt",
            upsample_model_name=super_resolution
        )

    else: # elif task == "multi_object_tracking":
        raise NotImplementedError("Multi-object tracking is not yet supported.")

    # feed files to model
    outputs = model.forward(files)

    # save output images to "runs/detect/exp"
    output_files = save_outputs(outputs)


    return [
        gr.Gallery(label="Outputs", value=[(f, f"ele_{i}") for i,f in enumerate(output_files)]),
        gr.DownloadButton(label="Download", value=output_files[0])
    ]


interface = gr.Interface(
    fn=main,
    inputs=[
        gr.Files(label="Images", file_count="multiple"),
        gr.Radio(
            ["", "ABPN", "ESRGAN"],
            label="super_resolution",
        ),
        gr.Radio(
            ["object_detection"],
            label="task",
        )
    ],
    outputs=[
        "gallery",
        gr.DownloadButton(),
    ],
    title="Benthic Object Detection with Super Resolution",
    description="Object detection focused on benthic images with super resolution capabilities."
)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--server-name", type=str, default=SERVER_NAME)
    parser.add_argument("--server-port", type=int, default=SERVER_PORT)
    args = parser.parse_args()

    SERVER_NAME = args.server_name
    SERVER_PORT = args.server_port
    
    interface.launch(server_name=SERVER_NAME, server_port=SERVER_PORT)