from PIL import Image

def crop_gif(input_file, output_file, x1, y1, x2, y2):
    # Open the GIF file
    gif = Image.open(input_file)

    # Extract each frame of the GIF
    frames = []
    for frame in range(0, gif.n_frames):
        gif.seek(frame)
        frames.append(gif.copy())

    # Crop each frame
    cropped_frames = []
    for frame in frames:
        cropped_frame = frame.crop((x1, y1, x2, y2))
        cropped_frames.append(cropped_frame)
  
    # Trim frames
    final_frames = cropped_frames[:65]


    # Save the cropped frames as a new GIF
    final_frames[0].save(output_file, save_all=True, append_images=final_frames[1:], loop=0)

# Replace 'input.gif', 'output_cropped.gif' with your file names
# Replace x1, y1, x2, y2 with the coordinates of the top-left and bottom-right corners of the crop region
crop_gif('../data/example/aquarium_032_mot.gif', '../data/example/aquarium_032_mot_cropped.gif', x1=100, y1=70, x2=1750, y2=1080)