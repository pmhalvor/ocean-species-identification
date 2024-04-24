from fathomnet.models.yolov5 import YOLOv5Model
from pathlib import Path
from PIL import Image
from PIL import ImageOps
from typing import List, Union

import cv2
import numpy as np
import onnxruntime
import os
import torch 

# ABPN imports 
from tqdm.auto import tqdm

# ESRGAN imports 
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
# import basicsr.data.degradations  # comment out line 8

# # HAT imports (installed via scripts/get_hat.sh)
# from hat.archs.hat_arch import HAT


class ABPN(torch.nn.Module):
    def __init__(
            self, 
            model_path: str="/models/sr_mobile_python/models_modelx4.ort", 
            store:bool=True
        ):
        self.model_path = model_path
        self.saved_imgs = {}
        self.store = store

    def pre_process(self, img: np.array) -> np.array:
        # H, W, C -> C, H, W
        img = np.transpose(img[:, :, 0:3], (2, 0, 1))
        # C, H, W -> 1, C, H, W
        img = np.expand_dims(img, axis=0).astype(np.float32)
        return img


    def post_process(self, img: np.array) -> np.array:
        # 1, C, H, W -> C, H, W
        img = np.squeeze(img)
        # C, H, W -> H, W, C
        img = np.transpose(img, (1, 2, 0))
        return img


    def save(self, img: np.array, save_name: str) -> None:
        # cv2.imwrite(save_name, img)
        if self.store:
            self.saved_imgs[save_name] = img


    def inference(self, img_array: np.array) -> np.array:
        print("Inference", self.model_path)
        # unasure about ability to train an onnx model from a Mac
        ort_session = onnxruntime.InferenceSession(self.model_path)
        ort_inputs = {ort_session.get_inputs()[0].name: img_array}
        ort_outs = ort_session.run(None, ort_inputs)

        return ort_outs[0]


    def upsample(self, image_paths: List[str]):
        outputs = []

        for image_path in tqdm(image_paths):

            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            # filename = os.path.basename(image_path)

            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            if img.shape[2] == 4:
                alpha = img[:, :, 3]  # GRAY
                alpha = cv2.cvtColor(alpha, cv2.COLOR_GRAY2BGR)  # BGR
                alpha_output = self.post_process(
                    self.inference(self.pre_process(alpha))
                )  # BGR
                alpha_output = cv2.cvtColor(alpha_output, cv2.COLOR_BGR2GRAY)  # GRAY

                img = img[:, :, 0:3]  # BGR
                image_output = self.post_process(
                    self.inference(self.pre_process(img))
                )  # BGR
                output_img = cv2.cvtColor(image_output, cv2.COLOR_BGR2BGRA)  # BGRA
                output_img[:, :, 3] = alpha_output
                self.save(output_img, Path(image_path).stem)

            elif img.shape[2] == 3:
                image_output = self.post_process(
                    self.inference(self.pre_process(img))
                )  # BGR
                self.save(image_output, Path(image_path).stem)

            outputs += [image_output.astype('uint8')]

        return outputs


    def enhance(self, img: np.array) -> np.array:
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        if img.shape[2] == 4:
            alpha = img[:, :, 3]  # GRAY
            alpha = cv2.cvtColor(alpha, cv2.COLOR_GRAY2BGR)  # BGR
            alpha_output = self.post_process(
                self.inference(self.pre_process(alpha))
            )  # BGR
            alpha_output = cv2.cvtColor(alpha_output, cv2.COLOR_BGR2GRAY)  # GRAY

            img = img[:, :, 0:3]  # BGR
            image_output = self.post_process(
                self.inference(self.pre_process(img))
            )  # BGR
            output_img = cv2.cvtColor(image_output, cv2.COLOR_BGR2BGRA)  # BGRA
            output_img[:, :, 3] = alpha_output
            # self.save(output_img, Path(image_path).stem)

        elif img.shape[2] == 3:
            image_output = self.post_process(
                self.inference(self.pre_process(img))
            )  # BGR
            # self.save(image_output, Path(image_path).stem)
        
        return img, "BGR"


class ESRGAN(torch.nn.Module):
    def __init__(
        self, 
        model_name: str="realesr-general-x4v3", 
        model_dir: str="/models",
        tile=0, 
        tile_pad=10, 
        pre_pad=0, 
        half=False, 
        device=None
    ):
        super(ESRGAN, self).__init__()
        # model path and name
        self.model_dir = model_dir
        self.model_path  = os.path.join(model_dir, model_name + '.pth') 
        self.model_name = model_name
        self.check_model_present()

        # RRDN parameters specific to pretrained model instance: v0.1.0/RealESRGAN_x4plus
        self.model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)

        # other model parameters
        self.netscale = 4
        self.tile = tile
        self.tile_pad = tile_pad
        self.pre_pad = pre_pad
        self.half = half

        # acutal sr module
        self.upsampler = RealESRGANer(
            scale=self.netscale,
            model_path=self.model_path,
            model=self.model,
            tile=self.tile,
            tile_pad=self.tile_pad,
            pre_pad=self.pre_pad,
            half=self.half
        )

        # realesrgan tries to cast to cuda, but not mps for Mac users 
        if device:
            self.device = torch.device(device)
            self.upsampler.device = torch.device(device)
            self.upsampler.model = self.upsampler.model.to(torch.device(device))


    def upsample(self, image_paths: List[str]):
        outputs = []

        for image_path in tqdm(image_paths):
            img = Image.open(image_path)
            img = np.array(img)
            img = self.enhance(img)[0]  # 2nd dim not needed, specifies output type 'RGB
            outputs += [img]

        return outputs
    

    def enhance(self, img: np.array) -> np.array:
        return self.upsampler.enhance(img)


    def check_model_present(self):
        # sanity check before proceeding
        if not os.path.isfile(self.model_path):
            raise ValueError(
                f"Model {self.model_name} not found locally at \n" \
                f"{self.model_path}. \n" \
                "Download https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
            )


class Hat(torch.nn.Module):
    """
    Config for the pretrained instance we are using found at:
    https://github.com/XPixelGroup/HAT/blob/main/options/test/HAT_SRx4_ImageNet-pretrain.yml
    """

    def __init__(
        self, 
        weight_path: str = "/models/HAT/HAT_SRx4_ImageNet-pretrain.pth", 
        upscale = 4,
        in_chans = 3,
        img_size = 64,
        window_size = 16,
        compress_ratio = 3,
        squeeze_factor = 30,
        conv_scale = 0.01,
        overlap_ratio = 0.5,
        img_range = 1.,
        depths = [6, 6, 6, 6, 6, 6],
        embed_dim = 180,
        num_heads = [6, 6, 6, 6, 6, 6],
        mlp_ratio = 2,
        upsampler = 'pixelshuffle',
        resi_connection = '1conv',
        grad=False,
        verbose=False,
        device=None,
    ):
        raise NotImplementedError("HAT is not yet supported in this version of the library")
        super(Hat, self).__init__()
        self.model = HAT(
            upscale = upscale,
            in_chans = in_chans,
            img_size = img_size,
            window_size = window_size,
            compress_ratio = compress_ratio,
            squeeze_factor = squeeze_factor,
            conv_scale = conv_scale,
            overlap_ratio = overlap_ratio,
            img_range = img_range,
            depths = depths,
            embed_dim = embed_dim,
            num_heads = num_heads,
            mlp_ratio = mlp_ratio,
            upsampler = upsampler,
            resi_connection = resi_connection,
        )

        self.model.load_state_dict(torch.load(weight_path)['params_ema'])

        # cast to device
        if device:
            self.model.to(torch.device(device))
            self.device = device 
        else:
            self.device = self.model.device

        self.no_grad() if not grad else None
        self.verbose = verbose


    def set_device(self, device):
        self.model.to(torch.device(device))
        self.device = device


    def no_grad(self):
        self.model.eval()

        for param in self.model.parameters():
            param.requires_grad = False


    def crop_image(self, image, size):
        return ImageOps.fit(image, size, Image.LANCZOS)


    def resize_image(self, image, size):
        # Get the size of the current image
        old_size = image.size

        # Calculate the ratio of the new size and the old size
        ratio = min(float(size[i]) / float(old_size[i]) for i in range(len(size)))

        # Calculate the new size
        new_size = tuple([int(i*ratio) for i in old_size])

        # Resize the image
        image = image.resize(new_size, Image.LANCZOS)

        # Create a new image with the specified size and fill it with white color
        new_image = Image.new("RGB", size, "white")

        # Calculate the position to paste the resized image
        position = ((size[0] - new_size[0]) // 2, (size[1] - new_size[1]) // 2)

        # Paste the resized image to the new image
        new_image.paste(image, position)

        return new_image


    def upsample(self, image_paths: List[str]):

        outputs = []

        for image_path in tqdm(image_paths):
            # load image
            img = Image.open(image_path)
            img_shape = np.array(img).shape

            # crop image to size w/ factor of 16
            input_size = img_shape[0] - (img_shape[0] % 16)
            cropped_img = self.crop_image(img, (input_size, input_size))

            # prep image dimension order
            input_img = torch.tensor(np.array(cropped_img)).to(self.device).permute(2, 0, 1)

            # feed to model
            output_tensor = self.model.forward(input_img)

            # post process to maintain aspect ratio, ensuring labels are still accurate
            output_array = output_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
            output_img = Image.fromarray((output_array).astype(np.uint8)).convert('RGB')  
            scaled_output_size = (img_shape[1]*self.model.upscale, img_shape[0]*self.model.upscale)
            img = self.resize_image(output_img, scaled_output_size)

            outputs += [np.array(img)]

        return outputs
    

class YOLOv5ModelWithUpsample(YOLOv5Model, torch.nn.Module):
    def __init__(
            self, 
            detection_model_path: str = "/models/fathomnet_benthic/mbari-mb-benthic-33k.pt",  
            upsample_model: Union[ABPN, ESRGAN, Hat, None] = None,
            upsample_model_name: str = "",
        ):
        super().__init__(detection_model_path)

        self.upsample_model = None
        if upsample_model:
            self.upsample_model = upsample_model
        elif upsample_model_name:
            if upsample_model_name == "ABPN":
                self.upsample_model = ABPN(model_path="../models/sr_mobile_python/models_modelx4.ort")
            elif upsample_model_name == "ESRGAN":
                self.upsample_model = ESRGAN(
                    model_dir="../models/ESRGAN/",
                    model_name="RealESRGAN_x4plus"
                )
            elif upsample_model_name == "HAT":
                self.upsample_model = Hat()
            else:
                raise ValueError("Upsample model not recognized")

    def forward(self, X: List[str]):
        if self.upsample_model:
            print("Upsampling images...")
            X = self.upsample_model.upsample(X)
        return self._model(X)
    