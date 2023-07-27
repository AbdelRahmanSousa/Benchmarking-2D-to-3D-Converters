from model import ConstructorModel
import json
import numpy as np
import os
import torch
import torch.backends.cudnn
import torch.utils.data

import Pix2VoxUtils.utils.binvox_visualization as binvox_visualization
import Pix2VoxUtils.utils.data_loaders as data_loaders
import Pix2VoxUtils.utils.data_transforms as data_transforms
import Pix2VoxUtils.utils.network_utils as network_utils

from datetime import datetime as dt
from Pix2VoxUtils.config import cfg
from Pix2VoxUtils.models.encoder import Encoder
from Pix2VoxUtils.models.decoder import Decoder
from Pix2VoxUtils.models.refiner import Refiner
from Pix2VoxUtils.models.merger import Merger


class Pix2Vox(ConstructorModel):
    path: str

    def __init__(self, path: str):
        self.cfg = cfg
        cfg.CONST.WEIGHTS = path
        self.encoder = Encoder(self.cfg)
        self.decoder = Decoder(self.cfg)
        self.refiner = Refiner(self.cfg)
        self.merger = Merger(self.cfg)
        if torch.cuda.is_available():
            self.encoder = torch.nn.DataParallel(self.encoder).cuda()
            self.decoder = torch.nn.DataParallel(self.decoder).cuda()
            self.refiner = torch.nn.DataParallel(self.refiner).cuda()
            self.merger = torch.nn.DataParallel(self.merger).cuda()
        print('[INFO] %s Loading weights from %s ...' % (dt.now(), cfg.CONST.WEIGHTS))
        checkpoint = torch.load(cfg.CONST.WEIGHTS)
        epoch_idx = checkpoint['epoch_idx']
        self.encoder.load_state_dict(checkpoint['encoder_state_dict'])
        self.decoder.load_state_dict(checkpoint['decoder_state_dict'])
        if cfg.NETWORK.USE_REFINER:
            self.refiner.load_state_dict(checkpoint['refiner_state_dict'])
        if cfg.NETWORK.USE_MERGER:
            self.merger.load_state_dict(checkpoint['merger_state_dict'])
        self.encoder.eval()
        self.decoder.eval()
        self.refiner.eval()
        self.merger.eval()

    def convert(self, images):
        # Load images
        # TODO Pytorch images loader
        # Pass images to NN
        torch.backends.cudnn.benchmark = True
        # Test the encoder, decoder, refiner and merger
        image_features = self.encoder(rendering_images)
        raw_features, generated_volume = self.decoder(image_features)
        if cfg.NETWORK.USE_MERGER:
            generated_volume = self.merger(raw_features, generated_volume)
        else:
            generated_volume = torch.mean(generated_volume, dim=1)
        if cfg.NETWORK.USE_REFINER:
            generated_volume = self.refiner(generated_volume)
        # TODO save voxels and return path


















