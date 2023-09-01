from scipy.integrate import trapezoid
from numpy import loadtxt
from os.path import join


def get_TUV_information(
    params: dict,
    filename: str,
) -> float:
    filename = join(
        params["data_path"],
        "TUV",
        filename
    )
    wavelength, direct, diffuse = loadtxt(
        filename,
        max_rows=110,
        skiprows=18,
        unpack=True,
        usecols=[
            0,
            2,
            3
        ],
    )
    wavelength = wavelength+0.5
    direct = trapezoid(
        direct,
        wavelength
    )
    diffuse = trapezoid(
        diffuse,
        wavelength,
    )
    return direct, diffuse
