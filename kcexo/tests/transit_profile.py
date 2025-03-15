from pathlib import Path
import yaml
from astropy.time import Time


from kcexo.data.exoclock_data import ExoClockData
from kcexo.observatory import Observatories, Observatory



if __name__ == '__main__':
    with open("./data/observatories.yaml", "r", encoding="utf-8") as f:
        obss_y = yaml.safe_load(f)
    obss: Observatories = Observatories(obss_y)
    ob: Observatory = obss.observatories['Ickenham Observatory']
    exoclock_path = Path(".")
    exd: ExoClockData = ExoClockData(exoclock_path)
    all_transits = exd.get_transits(Time("2025-03-15 16:00"), Time("2025-04-16 08:00"), ob, True, True)
