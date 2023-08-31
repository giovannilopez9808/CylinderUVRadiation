from scipy.integrate import trapezoid
from numpy import loadtxt
from os.path import join


def get_extraterrestial_UV(params: dict) -> float:
    filename = "extraterrestial_spectrum.dat"
    filename = join(
        params["data_path"],
        filename
    )
    wavelength, spectrum = loadtxt(
        filename,
        skiprows=2,
        unpack=True,
    )
    wavelength = wavelength/10
    index = (wavelength >= 290) & (wavelength <= 400)
    wavelength = wavelength[index]
    spectrum = spectrum[index]
    integral = trapezoid(
        spectrum,
        wavelength,
    )
    return integral
