from torch.utils.data.dataset import Dataset
import numpy as np
import cv2


class ReconstructionDataset(Dataset):
    def __init__(self, images, transforms=None):
        self.image_paths = images
        self.transforms = transforms

    def __len__(self):
        return 1

    def __getitem__(self, index):
        images = []
        for image_path in self.image_paths:
            images.append(cv2.imread(image_path, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.)
        images = np.asarray(images)
        if self.transforms:
            images = self.transforms(images)
        return images