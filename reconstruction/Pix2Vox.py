from .model import ConstructorModel
import json
import numpy as np
import uuid
import os
import torch
import torch.backends.cudnn
from torch.utils.data import DataLoader, Dataset
from .Pix2VoxUtils.utils.binvox_rw import Voxels
from .Pix2VoxUtils.utils.binvox_visualization import get_volume_views
from .Pix2VoxUtils.utils.data_transforms import CenterCrop, Normalize, RandomBackground, ToTensor, Compose
from .Pix2VoxUtils.utils.network_utils import var_or_cuda
from datetime import datetime as dt
from .Pix2VoxUtils.config import cfg
from .Pix2VoxUtils.models.encoder import Encoder
from .Pix2VoxUtils.models.decoder import Decoder
from .Pix2VoxUtils.models.refiner import Refiner
from .Pix2VoxUtils.models.merger import Merger
from .reconstruction_dataset import ReconstructionDataset


class Pix2Vox(ConstructorModel):
    path: str

    def __init__(self, path: str):
        self.cfg = cfg
        # Save full model path
        cfg.CONST.WEIGHTS = os.path.join(path, 'Pix2Vox-A-ShapeNet.pth')
        # Initialize network
        self.encoder = Encoder(self.cfg)
        self.decoder = Decoder(self.cfg)
        self.refiner = Refiner(self.cfg)
        self.merger = Merger(self.cfg)
        # Accelerate network using CUDA if available
        if torch.cuda.is_available():
            self.encoder = torch.nn.DataParallel(self.encoder).cuda()
            self.decoder = torch.nn.DataParallel(self.decoder).cuda()
            self.refiner = torch.nn.DataParallel(self.refiner).cuda()
            self.merger = torch.nn.DataParallel(self.merger).cuda()
        # Load model and update network sate
        checkpoint = torch.load(cfg.CONST.WEIGHTS)
        epoch_idx = checkpoint['epoch_idx']
        self.encoder.load_state_dict(checkpoint['encoder_state_dict'])
        self.decoder.load_state_dict(checkpoint['decoder_state_dict'])
        if cfg.NETWORK.USE_REFINER:
            self.refiner.load_state_dict(checkpoint['refiner_state_dict'])
        if cfg.NETWORK.USE_MERGER:
            self.merger.load_state_dict(checkpoint['merger_state_dict'])
        # Set network mode to evaluate
        self.encoder.eval()
        self.decoder.eval()
        self.refiner.eval()
        self.merger.eval()

    def convert(self, images):
        # Load images
        IMG_SIZE = cfg.CONST.IMG_H, cfg.CONST.IMG_W
        CROP_SIZE = cfg.CONST.CROP_IMG_H, cfg.CONST.CROP_IMG_W
        transforms = Compose([
            CenterCrop(IMG_SIZE, CROP_SIZE),
            RandomBackground(cfg.TEST.RANDOM_BG_COLOR_RANGE),
            Normalize(mean=cfg.DATASET.MEAN, std=cfg.DATASET.STD),
            ToTensor(),
        ])
        loader = DataLoader(dataset=ReconstructionDataset(images, transforms=transforms),
                            batch_size=1,
                            num_workers=1,
                            pin_memory=True,
                            shuffle=False)
        # Pass images to NN
        torch.backends.cudnn.benchmark = True
        # Test the encoder, decoder, refiner and merger
        for id, rendering_images in enumerate(loader):
            with torch.no_grad():
                # Get data from data loader
                rendering_images = var_or_cuda(rendering_images)
                image_features = self.encoder(rendering_images)
                raw_features, generated_volume = self.decoder(image_features)
                generated_volume = self.merger(raw_features, generated_volume)
                generated_volume = self.refiner(generated_volume)
            # Save output to ./Target/(uuid).binvox
            voxel_data = generated_volume[0].cpu()
            voxel_data = voxel_data.numpy()
            dims = voxel_data.shape
            output_path = './Target/' + str(uuid.uuid4()) + '.binvox'
            Voxels(voxel_data.squeeze().__ge__(0.5), dims, translate=[0, 0, 0],
                   scale=0, axis_order='xyz').write(open(output_path, 'wb+'))
            return output_path
