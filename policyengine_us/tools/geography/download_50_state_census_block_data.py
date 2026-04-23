import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

STATE_NAMES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]
STATE_CODES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]
STATE_CODES = [x.lower() for x in STATE_CODES]
DATA_FOLDER = Path("data")
DOWNLOAD_TIMEOUT_SECONDS = 60
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
MAX_ARCHIVE_DOWNLOAD_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_MEMBER_COUNT = 64
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 512 * 1024 * 1024


def _download_with_limits(url: str, destination: Path) -> None:
    downloaded_bytes = 0

    try:
        with requests.get(
            url, stream=True, timeout=DOWNLOAD_TIMEOUT_SECONDS
        ) as response:
            response.raise_for_status()
            with Path(destination).open("wb") as file:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if not chunk:
                        continue
                    downloaded_bytes += len(chunk)
                    if downloaded_bytes > MAX_ARCHIVE_DOWNLOAD_BYTES:
                        raise ValueError(
                            f"Downloaded archive exceeds {MAX_ARCHIVE_DOWNLOAD_BYTES} bytes"
                        )
                    file.write(chunk)
    except Exception:
        Path(destination).unlink(missing_ok=True)
        raise


def _safe_extract(zip_ref: zipfile.ZipFile, destination: Path) -> None:
    """Extract an archive only if every member stays within the destination."""

    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    members = zip_ref.infolist()
    if len(members) > MAX_ARCHIVE_MEMBER_COUNT:
        raise ValueError(
            f"Archive contains {len(members)} files, exceeding the limit of "
            f"{MAX_ARCHIVE_MEMBER_COUNT}"
        )

    total_uncompressed_bytes = 0
    for member in members:
        total_uncompressed_bytes += member.file_size
        if total_uncompressed_bytes > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise ValueError(
                "Archive exceeds the allowed uncompressed size limit of "
                f"{MAX_ARCHIVE_UNCOMPRESSED_BYTES} bytes"
            )
        target_path = (destination / member.filename).resolve()
        if destination != target_path and destination not in target_path.parents:
            raise ValueError(f"Unsafe path in zip archive: {member.filename}")
    zip_ref.extractall(destination)


def download_state_block_data(data_folder: Path = DATA_FOLDER) -> pd.DataFrame:
    data_folder = Path(data_folder)
    data_folder.mkdir(parents=True, exist_ok=True)

    dfs = []
    for state_name, state_code in tqdm(
        zip(STATE_NAMES, STATE_CODES), desc="Downloading Census data"
    ):
        data_url = (
            "https://www2.census.gov/programs-surveys/decennial/2020/data/"
            f"01-Redistricting_File--PL_94-171/{state_name}/{state_code}2020.pl.zip"
        )
        zip_path = data_folder / f"{state_code}2020.pl.zip"
        extract_dir = data_folder / f"{state_code}2020.pl"

        _download_with_limits(data_url, zip_path)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            _safe_extract(zip_ref, extract_dir)

        os.remove(zip_path)

        df = pd.read_csv(
            extract_dir / f"{state_code}geo2020.pl",
            sep="|",
            low_memory=False,
            encoding="ISO-8859-1",
        )
        df["state"] = state_code
        dfs.append(df)

        full_df = pd.concat(dfs)
        full_df.to_csv(data_folder / "50_state_block_data.csv", index=False)
        shutil.rmtree(extract_dir)

    return full_df


def main() -> None:
    download_state_block_data(DATA_FOLDER)


if __name__ == "__main__":
    main()
