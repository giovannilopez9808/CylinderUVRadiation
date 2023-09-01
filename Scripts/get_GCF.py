"""
Modo de uso

python get_GCF.py -t # --aspect #
python get_GCF.py --tilt # --aspect #

Si no se especifica el angulo tilt (t) o el angulo aspect (a), estos toman el
valor predefinido que es 0

Al termino de la ejecución se crea un archivo en la ruta

../Results/GCF.csv
"""

from Modules.HayDavisModel import CylinderRadiation
from Modules.TUV import get_TUV_information
from Modules.SZAReader import SZAReader
from Modules.params import get_params
from argparse import ArgumentParser
from pandas import DataFrame
from os.path import join

parser = ArgumentParser()
# Lectura del tilt por terminal
parser.add_argument(
    "-t",
    "--tilt",
    default=0,
    type=float
)
# Lectura del aspect por terminal
parser.add_argument(
    "-a",
    "--aspect",
    default=0,
    type=float,
)
args = parser.parse_args()
params = get_params()
# Lectura del SZA y los dias disponibles
sza_reader = SZAReader(
    params
)
# Dias disponibles
dates = sza_reader.get_dates()
# Inicializacion de la tabla de resultados
results = DataFrame(
    columns=[
        "SZA",
        "Ets",
        "TUV",
    ]
)
for date in dates:
    # SZA diario
    sza = sza_reader.get_sza(
        date
    )
    # Inicializacion del modelo Hay and Davis
    model = CylinderRadiation(
        params,
        aspect=args.aspect,
        tilt=args.tilt,
    )
    # Nombre del archivo con la informacion del TUV
    filename = date.replace(
        "-", ""
    )
    # Lectura de la informacion del TUv
    direct, diffuse = get_TUV_information(
        params,
        filename
    )
    # Estimacion de la irradiancia solar sobre un cilindro
    ets = model.estimate(
        sza,
        direct,
        diffuse,
        0.03
    )
    # Guardado de los resultados
    results.loc[date] = [
        sza,
        ets,
        diffuse+direct
    ]
# Calculo de la GCF
results["GCF"] = results["Ets"]/results["TUV"]
results.index.name = "Date"
# Nombre del archivo de guardado
filename = "GCF.csv"
filename = join(
    params["results_path"],
    filename
)
# Guardado de la tabla
results.to_csv(
    filename
)
print(results)
