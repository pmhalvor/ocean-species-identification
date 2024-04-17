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

Let's head over to the [Docker Hub](https://hub.docker.com/) and search for an image to download.

### Pulling and pushing images
<!-- Download pytorch image -->


