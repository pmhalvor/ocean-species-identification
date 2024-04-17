# Containerization with Docker 
2024-04-17 <br>
[Per Halvorsen](https://perhalvorsen.com) | [GitHub](https://github.com/pmhalvor/ocean-species-identification) | [LinkedIn](https://www.linkedin.com/in/pmhalvor/)

---

## Abstract
In this note, we want to explore the basics of containerization with Docker.
To start the note off, some background terminology needed to understand these technologies is covered, basically summarizing the [Docker overview](https://docs.docker.com/get-started/overview/). 
From here, we introduce a small example project and go through the necessary steps to build custom images suited specifically to the needs of the project.
Iterating on these simpler images, we then wrap a simplified machine learning model with a GUI into a container and show how to run and interact with this locally. 
The note rounds off with some tips on how such a model would be deployed to a server. 

# Outline 
**[Introduction](#Introduction)**
* Problem definition
    * Scope 
    * Fields 
* Best solution
    * Basic idea of containerization
    * Runnable anywhere
    * Opportunities: local development runnable on cloud, or easily portable app, like a tool-box. 

Background
* Vocabulary: summarized notes from [Docker overview](https://docs.docker.com/get-started/overview/)
* Architecture
* Diagrams: from tutorial or draw own
* Local requirements
    * Docker Desktop
    * Docker Hub account
    * Installation
* Basic starter commands 
    * Browsing images 
    * Pushing and pulling 
    * Run examples 
    * Build custom images

Our simple example
* Use the img2vid.py file to start
* Bake into image and run as executable 
* Bake into a Gradio app, and run locally
* (Attempt) Run from server, or just mention and say “more on that later”

<!-- A template project
* Bare bones
* Scripts to build project  -->
<!-- 
Our complex example
* Prepare the image 
    * All repos necessary 
    * All configs necessary  -->

Conclusion
* Recap
* Future work
    * Deploy to server
    * More complex scenarios
        * Lightweight images using multistage build or alpine
        * More complex models: multiple-stage pipelines or multiple models
        * Running multiple containers using docker-compose
        * Networking and volumes using docker-compose
        * Dockerfile best practices


# Introduction

## Problem
In software development, it is often necessary to run code on different machines, with different operating systems, and with different dependency versions.
The underlying code is the same, but the environment in which it runs can vary significantly.
Some may argue that well-written code should be executable on any machine, but in reality, things are not always that simple.

Often, systems require specific drivers, modules, or libraries to run, or the code is written in a language that is not natively supported by the target machine.
[OS-level virtualization](https://en.wikipedia.org/wiki/Operating-system-level_virtualization) makes it possible to run multiple (even nested) operating systems on a single physical machine, providing the essential first steps towards solving the problem of cross-platform collaboration. 

However, even with virtual machines, the code still needs to be packaged and shipped with all its dependencies.
Dependency management within these systems can be a hassle, especially as outdated libraries become vulnerable to security threats, or as new versions of libraries break compatibility with existing code.

Many Python projects nowadays make use of package managers like [pip](https://pypi.org/project/pip/) or [conda](https://docs.conda.io/en/latest/) together with a `requirements.txt` file to manage and specify the exact versions of needed dependencies. 
Similar set-ups exist for other languages too, like [maven](https://maven.apache.org/) for Java/Scala or [cargo](https://doc.rust-lang.org/cargo/) for Rust, but these are not always enough to ensure that the code runs as expected on all machines.
Even with these package managers, the target machine would still need to have the correct version of the language runtime installed, which introduces another potential source of conflicts.

Transitioning from technical, project development to high-level, product management, the necessity for code to run the same way on different machines becomes even more critical.
Whether the product needs to be deployed to a server with a different OS than the development team's local machines or the product is to be handed over as an executable program to a client, the code should always run as expected, without any issues.

Now, what if I told you there exists a tool that can solve all these problems and more? 

<!-- Drumroll gif -->
<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGo2MmZvbXd2ZjAyM2d4bHY3OGZhdDNuYnFyOTN5dHZtNDZ2bDFuZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/MZGH2MEUcfjVvIm2oR/giphy.gif" width="400" height="400" style="display: block; margin: 0 auto;" />


## Solution
To solve this problem, we need a way to package code and its dependencies into a single, self-contained unit that can be run anywhere.
This is where containerization comes in.

An application can be packaged into a container, which is a portable environment that contains everything needed to properly execute the application.
This includes the code, runtime, system tools, libraries, and settings.
Since containers are isolated environments, they can run on any machine that supports containerization technology, without compatibility issues or dependencies.

# Docker 
The most popular containerization technology is [Docker](https://www.docker.com/), which provides a platform for developing, shipping, and running applications inside containers.
To understand how Docker works, it is necessary to learn the terminology describing [Docker objects](https://docs.docker.com/get-started/overview/#docker-objects).


## Terminology


**Essential**
(Need to know)

* **image:** A read-only template that contains the application code, runtime, libraries, and dependencies. Think of this as the filesystem snapshot, describing how the inside of the container should look.
* **container:** An image that is running as a process on the host machine. A container is an instance of an image, with its own filesystem, network, and process space. It can serve or execute whatever task the image was built for.
* **Dockerfile:** The text file that contains instructions for building a Docker image. Each line represents a "layer" in the image and is a step in the process of building the final image. Arguments here are typically commands that would be run in a terminal to set up the environment for the application: defining environment variables, installs, cloning repositories, et cetera.
* **build:** The process of creating a Docker image from a Dockerfile. This involves downloading the necessary files, installing dependencies, and configuring the image according to the instructions in the Dockerfile.

**Additional**
(Good to know)

* **registry:** A library of different Docker images, such as [Docker Hub](https://hub.docker.com/), where public images are stored and shared. Docker Hub is the default registry for Docker images, and it is where you can find official images for many popular software packages, like databases, web servers, and programming languages. Private companies may maintain private registries, where internal images are managed and stored for proprietary or security reasons.
* **repository:** A collection of related Docker images (likely from the same project), tagged with version numbers. As updates are made to the project, new images including the updates are built and released under new version tags. This helps to keep track of changes and maintain a history of the project, in addition to dependency management. 
* **volume:** A persistent data storage mechanism for containers. Since containers are stateless (i.e. any data generated when running the container is deleted on container exit), volumes provide a way to store and share data between containers and the host machine. This is useful for storing configuration files, logs, or databases that need to persist across container restarts.
* **network:** A communication channel between containers. Different network types can be created to allow containers to communicate with each other, with the host machine, or with the rest of the internet. This is useful for creating microservices architectures, where different containers handle different parts of an application and need to communicate with each other.


## Architecture 
Docker containers are similar to virtual machines, but they are more lightweight and faster to start.
They share the host operating system's kernel and run as a nested process, isolated from other containers and the host system, making them more efficient than full virtual machines.

With the Docker client (`docker`), containers can be easily built, run, shared, and deleted, making them ideal for development, testing, and deployment.
This CLI is the fastest way to interact with Docker, but there are also GUIs available, like [Docker Desktop](https://www.docker.com/products/docker-desktop), which provides a graphical interface for managing containers, images, networks, and volumes.
Docker desktop is usually bundled with the Docker engine, which is the underlying software that runs and manages containers on the host machine.


The Docker client communicates with the Docker daemon (`dockerd`), which is responsible for managing containers, images, networks, and volumes on the host machine.
The daemon listens for API requests and manages the container lifecycle, including starting, stopping, and deleting containers, as well as building, pushing, and pulling images.


<img src="https://docs.docker.com/get-started/images/docker-architecture.webp" width="500" style="display: block; margin: 0 auto;" />
<div style="text-align:center;"><i>For more on its architecture see the <a href="https://docs.docker.com/get-started/overview/#docker-architecture">Docker overview</a>.</i></div>


## Local requirements
To get started with Docker, you need to have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your local machine.
The tool is free for teams under 250 or less than $10 million in annual revenue, and it is available for Windows, Mac, and Linux operating systems.

In addition to the Docker Desktop, it could be useful to have a [Docker Hub](https://hub.docker.com/).
This is a cloud-based registry where you can store and share Docker images, either publicly or privately.
It is also a place to find official images for popular software packages, as well as community-contributed images for a wide range of applications.
If you only plan on using others' images, then you don't need an account. 
However, if you are going to want to push your own images to the registry, making them openly available to others, then you will need an account.

<!-- Local login ? -->
If you've downloaded Docker Desktop, you should be able to run the `docker` command in your terminal.
You can easily log in to your Docker Hub account by running `docker login` and entering your credentials.

```
$ docker login

Login with your Docker ID to push and pull images from Docker Hub. If you don't have a Docker ID, head over to https://hub.docker.com to create one.
Username: your-docker-id
Password: **************
```

This will allow you to push and pull images from the registry, as well as manage your account settings.
Alternatively, you can log in through the Docker Desktop GUI.

<img src="../img/DockerDesktop.png" width="500" style="display: block; margin: 0 auto;" />


## Basic commands 

### Browsing images

To see what images are available on your local machine, you can run the following command:

```
$ docker images
```

This will list all the images that have been downloaded or built on your machine.
If you've just downloaded Docker Desktop, you probably won't have any images yet.

Let's head over to the [Docker Hub](https://hub.docker.com/) and find an image to download.

### Pulling and pushing images
<!-- Download pytorch image -->
Since we have been working with Python 3.11 for other parts of this series, let's pull an official Python image from [Docker Hub](https://hub.docker.com/_/python). 
For easy compatibility, we will pull the `bullseye` tag, which is based on Debian 11. 
If we were looking for a smaller image, we could have chosen the `slim` tag, which is based on Debian 11 slim, or better yet the `alpine` tag, which is typically used for lightweight images.

```
$ docker pull python:3.11-bullseye

3.11.9-bullseye: Pulling from library/python
197947a07d5f: Pull complete
31e3f4a53068: Pull complete
27317b8832e1: Pull complete
191dceb3c577: Pull complete
e2c5617071f9: Pull complete
82bfb246d40b: Pull complete
a8322d0f73c0: Pull complete
16945523aa37: Pull complete
Digest: sha256:8d7733affcd43dd64c072a0c22a731255326cec3683ff0ef616d9041d364aa1d
Status: Downloaded newer image for python:3.11.9-bullseye
docker.io/library/python:3.11.9-bullseye
```

Up until this point, we've been talking about containers as some application or executable that we want to run.
But this image is just a Python environment, not an application.
There's no program in it yet, just an empty filesystem with Python installed.
We can run this image as a container, and see what happens.

```bash
$ docker run python:3.11.9-bullseye
```

Nothing happens. 
<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjJxOXpwdHQwdHUza3d6NXBscGx5bHM2dnNjdG44ZHNqZm9xYjd4eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/TKXbwmrE0vkWmVFCUX/giphy.gif" width="400" height="400" style="display: block; margin: 0 auto;" />

That's because we didn't tell the container to do anything.
Let's try running Python instead.
To start, we'll just check the version. 

```bash
$ docker run python:3.11.9-bullseye python --version
Python 3.11.9
```

Great, but does this mean we can run a local Python script using the container?
Let's create a local Python file and test it out. 
```bash
$ echo "greet = lambda x,n: print(x*n); greet('hello world ', 2)" > greet.py
$ docker run python:3.11.9-bullseye python greet.py

python: can't open file '//greet.py': [Errno 2] No such file or directory
```
This won't work because the container doesn't have access to the local filesystem, hence the _isolated environments_ mentioned earlier.
The container can only  see inside its own filesystem, by default, but can be given access to the host filesystem using volumes. 
More on that later. 

Let's instead stick to the basics, and try to start a Python shell inside the container.

```python
$ docker run --rm -it python:3.11.9-bullseye python

Python 3.11.9 (main, Apr 10 2024, 11:55:03) [GCC 10.2.1 20210110] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.listdir()
['srv', 'boot', 'sys', 'lib', 'var', 'etc', 'root', 'tmp', 'mnt', 'run', 'proc', 'sbin', 'home', 'opt', 'bin', 'media', 'usr', 'dev', '.dockerenv']
```

Now we can see the internal files of the container.
If we are using another Linux based image, but without a Python installation, we could also just start a bash shell inside the container. 
This gives us the ability to check what is installed in the container, and potentially install new packages. 

```bash
$ docker run --rm -it debian:bullseye bash

root@f5cz1337a85e:/# ls

bin  boot  dev	etc  home  lib	media  mnt  opt  proc  root  run  sbin	srv  sys  tmp  usr  var
```

In our container, we can see that Python is installed, along with `git`, `curl`, `apt-get`, and other basic utilities that come with a Debian distribution. 



### Build custom images
So, the question then is, how can we then run a container with our own code inside? 
This is where the `Dockerfile` comes in.
<img src="../img/Dockerfile.png" width="500" style="display: block; margin: 0 auto;" />
<div style="text-align:center;">Source: <i>Understand Dockerfile by Rocky Chen (<a href="https://medium.com/swlh/understand-dockerfile-dd11746ed183">Medium</a>)</i></div>

Dockerfiles are text files that contain a series of instructions for building a Docker image.
They typically start with a `FROM` instruction, which specifies the base image to build upon.
This can be an official image from Docker Hub, like `python:3.11.9-bullseye`, or a custom image that you've built yourself.
There are no limits to how many instructions you can include in a Dockerfile, but it is recommended to keep them as minimal as possible to reduce the image size and build time.

It's typically a good idea to start with a base image that already has the necessary tools and libraries installed, and then add your own code and dependencies on top of that.
If your team typically using the same preprocessing steps or other common tasks, you could also consider creating a base image that includes these steps, and then build your application on top of that.

Here's an example of a simple Dockerfile that builds an image with Python 3.11.9 installed and our Python script `greet.py` made earlier, that prints "hello world" a few times.

```Dockerfile
# Use the official Python image as a parent image
FROM python:3.11.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy our file into the container at /app
COPY greet.py /app

# Run greet.py when the container launches
CMD ["python", "greet.py"]
```

To build the image, we can run the following command in the same directory as the `Dockerfile` and `greet.py` file:

```bash
$ docker build -t greet-app:1 .
```

This will create a new image called `greet-app` based on the instructions in the `Dockerfile`.
The image is currently only available on your local machine, but you can push it to Docker Hub or another registry to make it available to others.
Before we go that though, let's check it runs as expected.

```bash
$ docker run greet-app:1
hello world hello world
```

Sweet!
Let's now increase the complexity a bit more, by adding a Python script that takes in arguments. 
We can make some adjustments to our `greet.py` file from earlier, and call the new file `greet2.py`:

```python
def greet(x, n):
    print(x*n)

if __name__ == "__main__":
    import sys
    greet(sys.argv[1], int(sys.argv[2]))
```

We will need to revist our `Dockerfile` to include the new script, and configure it to allow arguments to be passed when running the container. 


```Dockerfile
# Use the official Python image as a parent image
FROM python:3.11.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the script into the container at /app
COPY greet2.py /app

# Run greet2.py when the container launches with ENTRYPOINT
ENTRYPOINT ["python", "greet2.py"]
```

Running this should give:
```bash
$ docker build -t greet-app:2 .
$ docker run greet2-app "hello earthling " 3

hello earthling hello earthling hello earthling
```

Now, we would like the container to be able to read in local files, as input data, do some transformation, then write output files _to our local machine_.
Remember, if we write to the container's filesystem, the data will be lost when the container exits (at the end of the run call).

We start by tweaking our Python script to write the output to a file, instead of printing it to the console. We'll call this one `greet3.py`: 

```python
def greet(x, n):
    print(x*n)
    return x*n

def write_greeting(x, n, output_file, ext="txt"):
    greeting = greet(x, n)
    with open(f"{output_file}.{ext}", "w") as f:
        f.write(x*n)

if __name__ == "__main__":
    import sys
    write_greeting(sys.argv[1], int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "output")
```

We'll also need to make some adjustments to our Dockerfile as well, to allow the container to write to the host filesystem.

```Dockerfile
# Use the official Python image as a parent image
FROM python:3.11.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the script into the container at /app
COPY greet3.py /app

# Run greet3.py when the container launches with ENTRYPOINT
ENTRYPOINT ["python", "greet3.py"]
```

To allow the container to write to the host filesystem, we need to use a volume.
Volumes are a way to persist data between container runs, and they can be used to share data between the host machine and the container.
To mount a volume, we can use the `-v` flag when running the container, specifying the path on the host machine where the data should be stored.

```bash
$ docker build -t greet-app:3 .
$ docker run -v $(pwd):/app greet-app:3 "hello alien " 3 "local_output"
$ cat local_output.txt

hello alien hello alien hello alien
```
With these basic functionalities in place, we can now move on to more complex tasks, relying on other libraries and tools.


# Our simple example
As a part of the exploration and discovery phase for a previous blog post on [multiple object tracking](https://perhalvorsen.com/media/notes/multiple_object_tracking.html), I created a small Python script that takes a series of images and converts them into a video, using the `opencv` library.
You can find the script at [src/tools/img2vid.py](https://github.com/pmhalvor/ocean-species-identification/blob/master/src/tools/img2vid.py).

This file can be used as such:
```bash
$ python3 img2video.py <file_pattern> <output_name>
```

To make this script more accessible, we can create a Docker image that runs the script as an executable.
This way, users don't need to have `opencv` installed on their local machine, or even Python for that matter.
They can simply run the Docker container with the input files and get the output video.

Let's start by creating a Dockerfile that builds an image with the `img2vid.py` script and the necessary dependencies installed.

```Dockerfile
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
```

We can build the image and run the container with the following commands:

```bash
$ docker build -t img2vid-app:1 .
$ docker run -v $(pwd)/../data/examples/:/app img2vid-app:1 "mba/*.jpg" "output.mp4"
```

To clarify, we are trying to mount the `data/examples/` directory from the parent directory of the current working directory, to the `/app` directory inside the container.
This way, the container can access the input files and write the output video to the host filesystem.




