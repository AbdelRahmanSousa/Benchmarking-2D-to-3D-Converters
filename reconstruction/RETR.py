from model import ConstructorModel
from torch import load


class RETR(ConstructorModel):
    path: str

    def __init__(self, path: str):
        self.model = load()

    def convert(self, images):
        pass