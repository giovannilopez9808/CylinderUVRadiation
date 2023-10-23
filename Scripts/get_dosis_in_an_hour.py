from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d
from scipy.integrate import trapezoid
from Modules.params import get_params
from argparse import ArgumentParser
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
    interpolation_data = CubicSpline(
        # interpolation_data = interp1d(
        hours,
        data,
        # fill_value="extrapolate"
    )
    hour_f = 13.5
    hours = arange(
        12.5,
        hour_f-delta,
        delta
    )
    data = interpolation_data(
        hours,
    )
    hours = hours*3600
    return hours, data


def decimal_hour_to_hhmm(hour: float) -> str:
    hour_ = int(hour)
    minute = int(hour % 1*60)+1
    return f"{hour_}:{minute}"


parser = ArgumentParser()
parser.add_argument(
    "--esa",
)
args = parser.parse_args()

params = get_params()
params.update({
    "phototypes": {
        "II": 250,
        "IV": 400,
    },
    "ESA": {
        "10": 0.202332235,
        "30": 0.6069967051
    }
})
esa = params["ESA"][args.esa]
delta = 1/3600
time = 3600
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
columns = list(
    params["phototypes"].keys()
)
# columns += ["Final time"]
results = DataFrame(
    columns=columns,
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
    hours, vit = get_second_resolution(
        hours,
        vit,
    )
    vit = vit*0.0035
    vit = vit*GCF_daily
    vit_t = vit[:time]
    VitD = trapezoid(
        vit_t,
        hours[:time],
        dx=delta,
    )
    hour_f = decimal_hour_to_hhmm(hours[-1]/3600)
    # results.loc[date, "Final time"] = hour_f
    for phototype, med in params["phototypes"].items():
        Dosis = VitD*esa*6153/med
        results.loc[date, phototype] = round(
            Dosis,
            1
        )
results = results.sort_index()
print(results/400)
filename = f"Doses_in_one_hour_esa_{args.esa}.csv"
filename = join(
    params["results_path"],
    filename
)
results.to_csv(
    filename,
)
