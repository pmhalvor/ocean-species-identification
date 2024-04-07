# Pipeline for species identification

This repository contains the work done exploring, evaluating, and training models for species identification in underwater images. 
The main goal is to play with and learn about the open-sourced models and datasets provided by the [Monterey Bay Aquarium Research Institute](https://www.mbari.org/).

## Contents
- [Exploring MBARI Benthic Object Detector](notebooks/mbari_benthic_object_detector.ipynb): This notebook explores the MBARI Benthic Object Detector, a YOLOv5 model trained to detect and classify species and objects in the Benthic zone. The notebook prepares for future work to apply a super-resolution model to input images.
([Link to readable html](https://perhalvorsen.com/media/notes/mbari_benthic_object_detector.html))

- [Super resolution experiment](notebooks/super_resolution_benthic_object_detection.ipynb): This notebook explores super-resolution models, some light-weight, some current state-of-the-art. We apply these models to our input images to a Benthic Object Detector, to see if we can improve performance without the need for fine-tuning. 
([Link to readable html](https://perhalvorsen.com/media/notes/super_resolution_benthic_object_detection.html))

- [Multiple Object Tracking](notebooks/multiple_object_tracking.ipynb): This notebook covers some foundational ideas around object tracking across multiple frames, and summarizes some state-of-the-art trackers. It finishes off with a simple implementation of the ByteTrack algorithm, uses the [`supervision`](https://github.com/roboflow/supervision) library, from [Roboflow](https://roboflow.com/).
([Link to readable html](https://perhalvorsen.com/media/notes/multiple_object_tracking.html))
