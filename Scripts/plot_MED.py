from Modules.params import get_params
from matplotlib import pyplot
from os.path import join
from os import listdir
from numpy import (
    loadtxt,
    arange,
)

params = get_params()
params.update({
    "Graphics": {
        "0305med.dat": {
            "color": "lightblue",
        },
        "1004med.dat": {
            "color": "pink",
        },
        "1007med.dat": {
            "color": "blue",
        },
        "1505med.dat": {
            "color": "green",
        },
        "1703med.dat": {
            "color": "r",
        },
        "2703med.dat": {
            "color": "orange",
        },
        "2704med.dat": {
            "color": "violet",
        },
    },
})
folder = join(
    params["data_path"],
    "MED"
)
files = listdir(folder)
pyplot.subplots(
    figsize=(
        12,
        6,
    )
)
for file in files:
    dataset = params["Graphics"][file]
    label = file[:4]
    label = label[:2]+"-"+label[2:]
    filename = join(
        folder,
        file
    )
    hours, _, vit = loadtxt(
        filename,
        unpack=True,
    )
    # UI/min to W/m2
    vit = vit*(210*4.3)/(3600*71)
    pyplot.plot(
        hours,
        vit,
        color=dataset["color"],
        label=label,
        marker="o",
        ls="--",
    )
# Añado el 0.5 para que lo incluya el 16.5 en la lista
hours = arange(
    9,
    16.5+0.5,
    0.5
)
# List Comprehension
hours_ticks = list(
    # si la hora tiene decimal
    f"{int(hour)}:30"
    if hour % 1
    # si la hora es entera
    else
    f"{int(hour)}:00"
    for hour in hours
)
pyplot.xlim(
    hours[0],
    hours[-1],
)
pyplot.ylim(
    0,
    0.18,
)
pyplot.xticks(
    hours,
    hours_ticks
)
pyplot.xlabel(
    'Tiempo (hs)'
)
pyplot.ylabel(
    'VITD3 ($W/m^2$)'
)
pyplot.grid(
    linestyle=':',
    linewidth=1
)
pyplot.legend()
pyplot.tight_layout()
pyplot.savefig(
    "MED.png"
)
