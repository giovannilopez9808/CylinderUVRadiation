from numpy import loadtxt


class Measurements:
    def __init__(
        self,
        params: dict,
    ) -> None:
        self.params = params
        self.hours = None
        self.vit = None
        self.uv = None

    def read(
        self,
        filename: str,
    ) -> tuple:
        hours, uv, vit = loadtxt(
            filename,
            unpack=True,
        )
        vit = vit*(210*4.3)/(3600*71)
