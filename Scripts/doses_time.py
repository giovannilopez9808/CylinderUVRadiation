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
    array,
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


def get_second_resolution(
    hours: array,
    data: array,
) -> tuple:
    interpolation_data = interp1d(
        hours,
        data,
    )
    hours = arange(
        12.5,
        hours[-1]-delta,
        delta
    )
    data = interpolation_data(
        hours,
    )
    hours = hours*3600
    return hours, data


params = get_params()
ESA10 = 0.202332235
ESA30 = 0.6069967051
delta = 1/3600
folder = join(
    params["data_path"],
    "MED"
)
files = get_filenames(
    folder,
)
filename = "GCF_tilt_000_aspect_000.csv"
filename = join(
    params["results_path"],
    filename,
)
GCF = read_csv(
    filename,
    index_col=0,
)
results = DataFrame(
    columns=[
        "Time"
    ]
)
results.columns.name = "Date"
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
    vit = vit*0.0035
    vit = vit*GCF_daily
    hours, vit = get_second_resolution(
        hours,
        vit,
    )
    Dosis = 0
    time = 1
    while Dosis < 400:
        vit_t = vit[:time]
        # a mano
        VitD = sum(
            (vit_t[1:]+vit_t[:-1])*delta/2
        )
        # con scipy
        VitD = trapezoid(
            vit_t,
            hours[:time],
            dx=delta,
        )
        Dosis = VitD*ESA10*6153/250
        time += 60
    time = (hours[time]-hours[0])/60
    results.loc[date] = time
results = results.sort_index()
filename = "Doses_time.csv"
filename = join(
    params["results_path"],
    filename
)
results.to_csv(
    filename,
)
print(results)
