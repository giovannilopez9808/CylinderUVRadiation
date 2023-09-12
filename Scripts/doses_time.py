from scipy.interpolate import interp1d
from scipy.integrate import trapezoid
from Modules.params import get_params
from os.path import join
from os import listdir
from pandas import (
    DataFrame,
    read_csv,
)
from numpy import (
    loadtxt,
    arange,
)


def get_date_from_filename(file: str) -> str:
    filename = file.split("/")
    filename = filename[-1]
    month = filename[2:4]
    month = month.zfill(2)
    day = filename[:2]
    day = day.zfill(2)
    date = f"2023-{month}-{day}"
    return date


def get_filenames(path: str) -> list:
    files = listdir(
        path
    )
    return files


params = get_params()
ESA10 = 0.202332235
ESA30 = 0.6069967051
delta = 1/60
folder = join(
    params["data_path"],
    "MED"
)
files = get_filenames(
    folder,
)
GCF = read_csv(
    "../Results/GCF_tilt_000_aspect_000.csv",
    index_col=0,
)
results = DataFrame(
    columns=[
        "Time"
    ]
)
results.index.name = "Date"
for file in files:
    file = join(
        folder,
        file
    )
    hours, _, vit = loadtxt(
        file,
        unpack=True,
    )
    date = get_date_from_filename(
        file
    )
    GCF_daily = GCF.loc[date]
    GCF_daily = GCF_daily["GCF"]
    # acá pasamos de Iu/min a W/m2
    vit = vit*((250*4.3)/(3600*71))
    # Agregamos la sección dedicada a la interpolación:
    vit_model = interp1d(
        hours,
        vit,
    )
    hours = arange(
        12.5,
        hours[-1]-delta,
        delta
    )
    vit = vit_model(
        hours
    )
    Dosis = 0
    time = 1
    while (Dosis < 400):
        # a mano
        vit_t = vit[:time]
        VitD = vit_t[1:]+vit_t[:-1]
        VitD = VitD*delta/2
        VitD = sum(VitD)*len(vit_t)**2
        # con scipy
        VitD = trapezoid(
            vit_t,
            hours[:time],
            dx=delta,
        )*len(vit_t)**2
        Dosis = 6153*GCF_daily*VitD*ESA10/250
        time += 1
    time = (hours[time]-hours[0])*60
    results.loc[date] = time
results = results.sort_index()
print(results)
