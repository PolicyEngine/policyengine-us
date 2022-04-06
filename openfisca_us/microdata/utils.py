import shutil
from pathlib import Path
import shutil
import pandas as pd
import re
import os
import h5py
import requests
from tqdm import tqdm
import numpy as np

US = "openfisca_us"


class classproperty(object):
    """Create a @classproperty decorator as explained in SO Post 5189699"""

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def dataset(cls):
    """Decorator function adding functionality to raw data source classes

    Args:
        cls (a Python class): A Python class that has the generate() function
        implemented

    This function is used on a raw data source class:

        newClass = dataset(RawClass)

    or, equivalently

    @dataset
    class RawClass:
        ...
    """

    def generate():
        raise NotImplementedError("No dataset generation function specified")

    if not hasattr(cls, "model"):
        cls.model = None
        cls.data_dir = data_folder(DATA_DIR / "external")
    else:
        cls.data_dir = data_folder(DATA_DIR / cls.model)

    def years(cl):
        pattern = re.compile(f"\n{cl.name}_([0-9]+).h5")
        matches = list(
            map(
                int,
                pattern.findall(
                    "\n"
                    + "\n".join(
                        map(lambda path: path.name, cl.data_dir.iterdir())
                    )
                ),
            )
        )
        return matches

    cls.years = classproperty(years)

    def last_year(self):
        return sorted(cls.years)[-1]

    cls.last_year = property(last_year)

    def filename(year):
        return f"{cls.name}_{year}.h5"

    cls.filename = staticmethod(filename)

    def load(year, key: str = None, mode: str = "r") -> pd.DataFrame:
        file = cls.data_dir / cls.filename(year)
        if cls.model:
            if key is None:
                return h5py.File(file, mode=mode)
            else:
                with h5py.File(file, mode=mode) as f:
                    values = np.array(f[key])
                return values
        else:
            if key is None:
                return pd.HDFStore(file)
            else:
                with pd.HDFStore(file) as f:
                    values = f[key]
                return values

    def remove(year=None):
        if year is None:
            filenames = map(cls.filename(year), cls.years)
        else:
            filenames = (cls.filename(year),)
        for filename in filenames:
            filepath = cls.data_dir / filename
            if filepath.exists():
                os.remove(filepath)

    cls.remove = staticmethod(remove)

    def remove_first_then(generate_func):
        def new_generate_func(year, *args):
            cls.remove(year)
            return generate_func(year, *args)

        return new_generate_func

    if hasattr(cls, "generate"):
        cls.generate = staticmethod(remove_first_then(cls.generate))
    else:
        cls.generate = staticmethod(generate)

    cls.load = staticmethod(load)

    if not hasattr(cls, "input_reform_from_year"):
        cls.input_reform_from_year = lambda year: ()

    cls.file = staticmethod(lambda year: cls.data_dir / cls.filename(year))

    def save(data_file: str, year: int = 2018):
        if "https://" in data_file:
            response = requests.get(data_file, stream=True)
            total_size_in_bytes = int(
                response.headers.get("content-length", 0)
            )
            block_size = 1024  # 1 Kibibyte
            progress_bar = tqdm(
                total=total_size_in_bytes, unit="iB", unit_scale=True
            )
            with open(cls.file(year), "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
        else:
            shutil.copyfile(data_file, cls.file(year))

    if not hasattr(cls, "save"):
        cls.save = staticmethod(save)

    return cls


def data_folder(path: str, erase=False) -> Path:
    folder = Path(path)
    folder.mkdir(exist_ok=True, parents=True)
    if erase:
        shutil.rmtree(folder)
        folder.mkdir()
    return folder


def safe_rmdir(path: str):
    if Path(path).exists():
        shutil.rmtree(path)


PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / "microdata"
