from model import ConstructorModel


class Pix2Vix(ConstructorModel):
    path: str

    def __init__(self, path: str):
        self.path = path

    def convert(self, images):
        pass
