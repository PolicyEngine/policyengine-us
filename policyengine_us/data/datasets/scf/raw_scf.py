from io import BytesIO
from zipfile import ZipFile
from policyengine_core.data import Dataset
from policyengine_us.data.storage import STORAGE_FOLDER
import pandas as pd
import requests
import json
import os



class RawSCF(Dataset):
    name = "raw_scf"
    label = "Raw SCF"
    time_period = None
    data_format = Dataset.TABLES

    def generate(self) -> None:
        """
        Generates the raw SCF dataset.
        Saves as HDF file to self.file_path
        """
        VALID_YEARS = [
            1989,
            1992,
            1995,
            1998,
            2001,
            2004,
            2007,
            2010,
            2013,
            2016,
            2019,
            2022
        ]

        if self.time_period not in VALID_YEARS:
            raise ValueError(
                f"No raw SCF data URL known for year {self.time_period}."
            )

        url = f"https://www.federalreserve.gov/econres/files/scfp{self.time_period}s.zip"

        response = requests.get(url)
        if (not response.ok):
            raise FileNotFoundError(
                f"Problem encountered when fetching the data. HTTPcode: {response.status_code}"
            )

        data = BytesIO(response.content)
        with ZipFile(data) as archive:
            # Assume only one file
            stata_file_name = archive.namelist()[0]
            with archive.open(stata_file_name) as stata_file:
                df = pd.read_stata(stata_file)
        
        # Save to HDF
        with pd.HDFStore( self.file_path, mode="w" ) as storage:
            storage['household'] = df

        # Log success
        print( f'Downloaded and saved SCF data for {self.time_period} to {self.file_path}')

class RawSCF_2022(RawSCF):
    time_period = 2022
    name      = f"raw_scf_{time_period}"
    label     = f"Raw SCF {time_period}"
    file_path = os.path.join( STORAGE_FOLDER, f"raw_scf_{time_period}.h5" )


