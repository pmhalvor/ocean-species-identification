# Use the official Python image as a parent image
FROM python:3.11.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the script into the container at /app
COPY img2vid.py /app

# Install the necessary dependencies
RUN pip install opencv-python

# Run img2vid.py when the container launches
ENTRYPOINT ["python", "img2vid.py"]