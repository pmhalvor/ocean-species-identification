# Stage 1: Prepare model weights
FROM python:3.11.9-bullseye AS model-prep

# Set the working directory inside the container
WORKDIR /models

# Copy the model weights into the container
COPY models /models

# Use the official Python image as a parent image
FROM python:3.11.9-bullseye

# Set local enivorment variable for server name and port
ENV SERVER_NAME "0.0.0.0"
ENV SERVER_PORT 7861

# Copy the repo into the container at current working directory
WORKDIR /app
COPY . .

# Copy models from the model-prep stage
COPY --from=model-prep /models /models

# Install the necessary dependencies for opencv and gradio
RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# Export the server port
EXPOSE $SERVER_PORT

# Update basicsr
RUN /bin/bash -c "source scripts/update_basicsr.sh"

# Run src/app.py when the container launches
CMD ["python3", "src/app.py"]