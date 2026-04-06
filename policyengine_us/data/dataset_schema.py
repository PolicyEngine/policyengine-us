import pandas as pd
from pathlib import Path

US_ENTITIES = [
    "person",
    "household",
    "tax_unit",
    "spm_unit",
    "family",
    "marital_unit",
]

# Only the 3 entities required for a minimal valid simulation.
# spm_unit, family, marital_unit are optional and default to empty.
_REQUIRED_ENTITIES = ("person", "household", "tax_unit")

# Sync with CURRENT_YEAR in system.py
_DEFAULT_TIME_PERIOD = 2024


class USSingleYearDataset:
    person: pd.DataFrame
    household: pd.DataFrame
    tax_unit: pd.DataFrame
    spm_unit: pd.DataFrame
    family: pd.DataFrame
    marital_unit: pd.DataFrame

    @staticmethod
    def validate_file_path(file_path: str, raise_exception: bool = True):
        if not file_path.endswith(".h5"):
            if raise_exception:
                raise ValueError(
                    "File path must end with '.h5' for USSingleYearDataset."
                )
            return False
        if not Path(file_path).exists():
            if raise_exception:
                raise FileNotFoundError(f"File not found: {file_path}")
            return False

        try:
            with pd.HDFStore(file_path, mode="r") as store:
                keys = {k.strip("/") for k in store.keys()}
                for name in _REQUIRED_ENTITIES:
                    if name not in keys:
                        if raise_exception:
                            raise ValueError(
                                f"Dataset '{name}' not found in: {file_path}"
                            )
                        return False
        except (OSError, IOError, KeyError, ValueError):
            if raise_exception:
                raise
            return False

        return True

    def __init__(
        self,
        file_path: str = None,
        person: pd.DataFrame = None,
        household: pd.DataFrame = None,
        tax_unit: pd.DataFrame = None,
        spm_unit: pd.DataFrame = None,
        family: pd.DataFrame = None,
        marital_unit: pd.DataFrame = None,
        time_period: int = _DEFAULT_TIME_PERIOD,
    ):
        file_path = str(file_path) if file_path else None
        if file_path is not None:
            self.validate_file_path(file_path)
            with pd.HDFStore(file_path, mode="r") as f:
                self.person = f["person"]
                self.household = f["household"]
                self.tax_unit = f["tax_unit"]
                self.spm_unit = f["spm_unit"] if "spm_unit" in f else pd.DataFrame()
                self.family = f["family"] if "family" in f else pd.DataFrame()
                self.marital_unit = (
                    f["marital_unit"] if "marital_unit" in f else pd.DataFrame()
                )
                if "_time_period" in f:
                    self.time_period = str(int(f["_time_period"].iloc[0]))
                else:
                    self.time_period = str(time_period)
        else:
            if person is None or household is None or tax_unit is None:
                raise ValueError(
                    "Must provide either a file path or at least "
                    "person, household, and tax_unit DataFrames."
                )
            self.person = person
            self.household = household
            self.tax_unit = tax_unit
            self.spm_unit = spm_unit if spm_unit is not None else pd.DataFrame()
            self.family = family if family is not None else pd.DataFrame()
            self.marital_unit = (
                marital_unit if marital_unit is not None else pd.DataFrame()
            )
            self.time_period = str(time_period)

        self.data_format = "arrays"
        self.tables = (
            self.person,
            self.household,
            self.tax_unit,
            self.spm_unit,
            self.family,
            self.marital_unit,
        )
        self.table_names = (
            "person",
            "household",
            "tax_unit",
            "spm_unit",
            "family",
            "marital_unit",
        )

    @property
    def name(self):
        return f"us_single_year_{self.time_period}"

    @property
    def label(self):
        return f"US Single Year Dataset ({self.time_period})"

    @property
    def file_path(self):
        """Stub for core compatibility. Returns None — callers that
        need a real path (e.g. macro_cache) should check first."""
        return None

    def save(self, file_path: str):
        Path(file_path).unlink(missing_ok=True)
        with pd.HDFStore(file_path) as f:
            for name, df in zip(self.table_names, self.tables):
                if len(df) > 0:
                    f.put(name, df, format="table", data_columns=True)
            f.put(
                "_time_period",
                pd.Series([int(self.time_period)]),
                format="table",
            )

    def load(self):
        data = {}
        for table_name, df in zip(self.table_names, self.tables):
            for col in df.columns:
                if col in data:
                    raise ValueError(
                        f"Duplicate column '{col}' found across "
                        f"entities. Cannot flatten to a single dict."
                    )
                data[col] = df[col].values
        return data

    def copy(self):
        return USSingleYearDataset(
            person=self.person.copy(),
            household=self.household.copy(),
            tax_unit=self.tax_unit.copy(),
            spm_unit=self.spm_unit.copy(),
            family=self.family.copy(),
            marital_unit=self.marital_unit.copy(),
            time_period=int(self.time_period),
        )


class USMultiYearDataset:
    def __init__(
        self,
        file_path: str = None,
        datasets: list[USSingleYearDataset] | None = None,
    ):
        if datasets is not None and file_path is not None:
            raise ValueError("Provide either datasets or file_path, not both.")

        if datasets is not None:
            self.datasets = {}
            for dataset in datasets:
                if not isinstance(dataset, USSingleYearDataset):
                    raise TypeError(
                        "All items in datasets must be of type USSingleYearDataset."
                    )
                year = int(dataset.time_period)
                self.datasets[year] = dataset
        elif file_path is not None:
            with pd.HDFStore(file_path, mode="r") as f:
                self.datasets = {}
                for key in f.keys():
                    if key.startswith("/person/"):
                        year = int(key.split("/")[2])
                        entity_dfs = {}
                        for entity in US_ENTITIES:
                            entity_key = f"/{entity}/{year}"
                            if entity_key in f:
                                entity_dfs[entity] = f[entity_key]
                            else:
                                entity_dfs[entity] = pd.DataFrame()
                        self.datasets[year] = USSingleYearDataset(
                            **entity_dfs,
                            time_period=year,
                        )
        else:
            raise ValueError("Must provide either datasets or file_path.")

        self.data_format = "time_period_arrays"
        self.time_period = str(min(self.datasets.keys()))

    @property
    def name(self):
        years = self.years
        return f"us_multi_year_{years[0]}_{years[-1]}"

    @property
    def label(self):
        years = self.years
        return f"US Multi Year Dataset ({years[0]}-{years[-1]})"

    @property
    def file_path(self):
        """Stub for core compatibility. Returns None — callers that
        need a real path (e.g. macro_cache) should check first."""
        return None

    def get_year(self, year: int) -> USSingleYearDataset:
        if year in self.datasets:
            return self.datasets[year]
        else:
            raise ValueError(f"No dataset found for year {year}.")

    @property
    def years(self):
        return sorted(self.datasets.keys())

    def __getitem__(self, year: int):
        return self.get_year(year)

    def save(self, file_path: str):
        Path(file_path).unlink(missing_ok=True)
        with pd.HDFStore(file_path) as f:
            for year, dataset in self.datasets.items():
                for name, df in zip(dataset.table_names, dataset.tables):
                    if len(df) > 0:
                        f.put(
                            f"{name}/{year}",
                            df,
                            format="table",
                            data_columns=True,
                        )
                f.put(
                    f"time_period/{year}",
                    pd.Series([year]),
                    format="table",
                    data_columns=True,
                )

    def copy(self):
        new_datasets = {year: dataset.copy() for year, dataset in self.datasets.items()}
        return USMultiYearDataset(datasets=list(new_datasets.values()))

    def load(self):
        data = {}
        for year, dataset in self.datasets.items():
            for table_name, df in zip(dataset.table_names, dataset.tables):
                for col in df.columns:
                    if col not in data:
                        data[col] = {}
                    elif year in data[col]:
                        raise ValueError(
                            f"Duplicate column '{col}' found across "
                            f"entities for year {year}. "
                            f"Cannot flatten to a single dict."
                        )
                    data[col][year] = df[col].values
        return data
