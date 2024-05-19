# Use the official Python image as a parent image
FROM python:3.11.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Set local enivorment variable for input and output dir
ENV INPUT_DIR /input
ENV OUTPUT_DIR /output

# Set local enivorment variable for server name and port
ENV SERVER_NAME "0.0.0.0"
ENV SERVER_PORT 7861

# Copy the scripts into the container at /app
COPY src/tools/img2vid.py /app
COPY src/tools/img2vid_gradio.py /app

# Install the necessary dependencies for opencv and gradio
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install opencv-python gradio

# Export the server port
EXPOSE $SERVER_PORT

# Run img2vid_gradio.py when the container launches
CMD ["python", "img2vid_gradio.py"]