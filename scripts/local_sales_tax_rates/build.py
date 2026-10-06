"""Build PolicyEngine-US locality sales tax rates from official files.

Writes `policyengine_us/data/local_sales_tax/rates.csv` and
`populations.csv`: the combined state and local general sales tax rate of
each county's places and of its area outside every place, for the states
whose locality rates are published in official files:

- the Streamlined Sales Tax (SST) member states with local sales taxes,
  from the rate and boundary files their revenue departments post on the
  SST Governing Board website under SSUTA sections 305 to 307;
- New York, from Publication 718 of the Department of Taxation and Finance,
  with rate history from Publication 718-A;
- Virginia, from Virginia Tax's "Sales and Use Tax Rates by Locality by
  Date" workbook.

Places and populations come from the 2020 Census redistricting (P.L.
94-171) block records. Each block takes the rate of the taxing unit it lies
in, and a place's rate is the population-weighted mean of its blocks'
rates. SOURCES.md in the output folder describes each source and its terms.

Usage:
    python scripts/local_sales_tax_rates/build.py --sources DIR [--download]

`--download` fetches every source into DIR first. Requires pandas, openpyxl
and pdftotext (poppler).
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import urllib.request
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = REPO / "policyengine_us" / "data" / "local_sales_tax"

# Rates are evaluated on the first day of each quarter from 2022 through 2026
# (SSUTA section 305 makes local rate and boundary changes effective only
# then) and on every other date in the window on which a state's files show
# a change: Tennessee, an associate member, changes rates on other dates, and
# so did Suffolk County, New York, on 1 Mar. 2025.
FIRST_DATE = date(2022, 1, 1)
LAST_DATE = date(2026, 10, 1)
WINDOW_END = pd.Timestamp("2026-12-31")

SST_URL = "https://www.streamlinedsalestax.org/ratesandboundry"
# SST member states: 23 full members and associate member Tennessee.
SST_STATES = {
    "AR": "05", "GA": "13", "IA": "19", "IN": "18", "KS": "20", "KY": "21",
    "MI": "26", "MN": "27", "NC": "37", "ND": "38", "NE": "31", "NJ": "34",
    "NV": "32", "OH": "39", "OK": "40", "RI": "44", "SD": "46", "TN": "47",
    "UT": "49", "VT": "50", "WA": "53", "WI": "55", "WV": "54", "WY": "56",
}  # fmt: skip
# SST states without a local general sales tax. The IRS has their residents
# enter no local sales tax (worksheet instruction after line 1), so they
# need no locality rates.
NO_LOCAL_TAX = {"IN", "KY", "MI", "NJ", "RI"}
VA_URL = (
    "https://www.tax.virginia.gov/sites/default/files/inline-files/"
    "sales-and-use-tax-rates-by-locality-by-date.xlsx"
)
NY_URLS = {
    "pub718.pdf": "https://www.tax.ny.gov/pdf/publications/sales/pub718.pdf",
    "pub718a.pdf": "https://www.tax.ny.gov/pdf/publications/sales/pub718a.pdf",
}
PL_URL = (
    "https://www2.census.gov/programs-surveys/decennial/2020/data/"
    "01-Redistricting_File--PL_94-171"
)
STATE_NAMES = {
    "AR": "Arkansas", "GA": "Georgia", "IA": "Iowa", "KS": "Kansas",
    "MN": "Minnesota", "NC": "North_Carolina", "ND": "North_Dakota",
    "NE": "Nebraska", "NV": "Nevada", "OH": "Ohio", "OK": "Oklahoma",
    "SD": "South_Dakota", "TN": "Tennessee", "UT": "Utah", "VT": "Vermont",
    "WA": "Washington", "WI": "Wisconsin", "WV": "West_Virginia",
    "WY": "Wyoming", "NY": "New_York", "VA": "Virginia",
}  # fmt: skip
N_SPECIAL = 20
# "End of time" dates in the SST files.
OPEN_ENDED = r"^(9999|2999|2099|2078)"
# Share of the ZIP codes the latest date's boundary records cover that a
# date's records must cover for that date's boundaries to be used (see
# sst_unit_rates). In the files retrieved for this build every state's
# records cover at least 95% from 2022 on; Nevada's 2025 address records
# added the 5%.
COMPLETE_SHARE = 0.9


def evaluation_dates() -> list[pd.Timestamp]:
    dates = []
    d = FIRST_DATE
    while d <= LAST_DATE:
        dates.append(pd.Timestamp(d))
        month = d.month + 3
        d = date(d.year + (month > 12), (month - 1) % 12 + 1, 1)
    return dates


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request) as response, open(path, "wb") as f:
        f.write(response.read())


def download(sources: Path) -> None:
    for kind in ["Rates", "Boundary"]:
        request = urllib.request.Request(
            f"{SST_URL}/{kind}/", headers={"User-Agent": "Mozilla/5.0"}
        )
        listing = urllib.request.urlopen(request).read().decode("latin-1")
        for href in re.findall(r'HREF="([^"]+)"', listing, flags=re.I):
            name = href.rsplit("/", 1)[-1]
            if name[:2] in SST_STATES and name.lower().endswith((".zip", ".csv")):
                fetch(
                    "https://www.streamlinedsalestax.org" + href,
                    sources / "sst" / kind.lower() / name,
                )
    for name, url in NY_URLS.items():
        fetch(url, sources / "ny" / name)
    fetch(VA_URL, sources / "va" / VA_URL.rsplit("/", 1)[-1])
    for abbr, name in STATE_NAMES.items():
        fetch(
            f"{PL_URL}/{name}/{abbr.lower()}2020.pl.zip",
            sources / "census" / "pl" / f"{abbr.lower()}2020.pl.zip",
        )
    (sources / "retrieved_at.txt").write_text(
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
    )


# --- SST ---------------------------------------------------------------------


def sst_file(sources: Path, kind: str, abbr: str) -> Path:
    """The state's rate or boundary file (one per state on the SST site)."""
    letter = {"rates": "R", "boundary": "B"}[kind]
    hits = sorted((sources / "sst" / kind).glob(f"{abbr}{letter}*"))
    assert len(hits) == 1, (abbr, kind, hits)
    return hits[0]


def read_sst_csv(path: Path, **kwargs):
    if path.suffix.lower() == ".zip":
        archive = zipfile.ZipFile(path)
        names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        assert len(names) == 1, (path, names)
        return pd.read_csv(archive.open(names[0]), **kwargs)
    return pd.read_csv(path, **kwargs)


def sst_dates(column: pd.Series) -> pd.Series:
    column = column.str.strip().str.replace(OPEN_ENDED, "2200", regex=True)
    return pd.to_datetime(column, format="%Y%m%d")


def load_sst_rates(sources: Path, abbr: str) -> pd.DataFrame:
    """SST rate file: one row per jurisdiction and effective period. Uses the
    general intrastate rate (column D of the SSTGB rate table)."""
    df = read_sst_csv(
        sst_file(sources, "rates", abbr),
        header=None,
        dtype=str,
        keep_default_na=False,
        encoding="latin-1",
        usecols=range(9),
    )
    df.columns = [
        "state", "jtype", "code", "general", "general_interstate",
        "food", "food_interstate", "begin", "end",
    ]  # fmt: skip
    df["jtype"] = df["jtype"].str.strip().str.zfill(2)
    df["code"] = df["code"].str.strip()
    df["rate"] = df["general"].astype(float)
    df["begin"] = sst_dates(df["begin"])
    df["end"] = sst_dates(df["end"])
    return df[["jtype", "code", "rate", "begin", "end"]]


def rate_lookup(rates: pd.DataFrame, when: pd.Timestamp) -> dict:
    """Rate of each (jurisdiction type, code) in effect on `when`. Where two
    rows overlap (a few files end a superseded row on the day its successor
    begins), the later-beginning row applies."""
    active = rates[(rates.begin <= when) & (rates.end >= when)]
    active = active.sort_values("begin").drop_duplicates(["jtype", "code"], keep="last")
    return {(t, c): r for t, c, r in zip(active.jtype, active.code, active.rate)}


BOUNDARY_COLUMNS = {
    0: "rtype", 1: "begin", 2: "end", 15: "zip", 17: "zip_low",
    22: "state", 23: "state_indicator", 24: "county", 25: "place",
}  # fmt: skip
for _k in range(N_SPECIAL):
    BOUNDARY_COLUMNS[30 + 3 * _k] = f"special{_k}"
    BOUNDARY_COLUMNS[31 + 3 * _k] = f"special{_k}_type"
SPECIALS = [(f"special{k}", f"special{k}_type") for k in range(N_SPECIAL)]
SIGNATURE = ["rtype", "begin", "end", "zip", "state_indicator", "county", "place"] + [
    column for pair in SPECIALS for column in pair
]
RECORD_TYPE_PRIORITY = {"A": 0, "4": 1, "Z": 2}


def load_sst_boundary(sources: Path, abbr: str) -> pd.DataFrame:
    """SST boundary file, keeping the columns that locate a record's taxing
    jurisdictions (SST Technology Guide, chapter 5, boundary table columns
    A-C, W-Z and AD-CK), collapsed to one row per distinct combination with
    its number of records. The collapsed file is cached next to the
    sources."""
    path = sst_file(sources, "boundary", abbr)
    cache = sources / "sst" / "cache" / f"{path.name.split('.')[0]}.pkl"
    if cache.exists():
        return pd.read_pickle(cache)
    parts = []
    reader = read_sst_csv(
        path,
        header=None,
        dtype=str,
        keep_default_na=False,
        encoding="latin-1",
        usecols=list(BOUNDARY_COLUMNS),
        on_bad_lines="skip",
        chunksize=200_000,
    )
    for chunk in reader:
        chunk = chunk.rename(columns=BOUNDARY_COLUMNS).drop(columns="state")
        for column in chunk.columns:
            chunk[column] = chunk[column].str.strip()
        # Some files start with a UTF-8 byte order mark.
        chunk["rtype"] = chunk["rtype"].str.replace("ï»¿", "").str.upper()
        chunk = chunk[chunk.rtype.isin(list(RECORD_TYPE_PRIORITY))]
        # The record's 5-digit ZIP code: column P for address records,
        # column R (zip code low) for ZIP records.
        chunk["zip"] = chunk["zip"].where(chunk.rtype == "A", chunk.zip_low).str[:5]
        chunk = chunk.drop(columns="zip_low")
        for code, kind in SPECIALS:
            chunk[kind] = chunk[kind].str.zfill(2).where(chunk[code] != "", "")
        parts.append(chunk.groupby(SIGNATURE).size().rename("records").reset_index())
    df = pd.concat(parts).groupby(SIGNATURE).records.sum().reset_index()
    df["begin"] = sst_dates(df["begin"])
    df["end"] = sst_dates(df["end"])
    cache.parent.mkdir(exist_ok=True)
    df.to_pickle(cache)
    return df


def sst_unit_rates(
    sources: Path, abbr: str, dates: list[pd.Timestamp], log: list
) -> pd.DataFrame:
    """Combined rate of each SST taxing unit at each date.

    A boundary record's combined rate sums the rates of the jurisdictions it
    lists (SST Technology Guide, chapter 5): the state, when the record's
    state indicator equals the state code; its county; its place; and up to
    20 special taxing districts. A unit is a county and the place code its
    records carry ("" for none). Its rate is the mean over its records, so a
    special district covering part of a unit counts in proportion to the
    records it covers. Each unit uses its finest record type: address (A)
    records, else ZIP+4 (4), else 5-digit ZIP (Z) records.
    """
    state_fips = SST_STATES[abbr]
    rates = load_sst_rates(sources, abbr)
    boundary = load_sst_boundary(sources, abbr)
    dates = change_dates(dates, [rates, boundary])
    # Files of states without county taxes may leave the county code empty;
    # such units are keyed by their place code alone (county "").
    boundary["county"] = (state_fips + boundary["county"].str.zfill(3)).where(
        boundary.county.str.strip("0") != "", ""
    )

    # Some boundary files keep no history before some date. A date's own
    # records are used if they cover at least COMPLETE_SHARE of the ZIP codes
    # the latest date's records cover; earlier dates use the first such
    # date's records, with the rates in effect on the date itself.
    def zips(d: pd.Timestamp) -> int:
        active = (boundary.begin <= d) & (boundary.end >= d)
        return boundary.zip[active].nunique()

    coverage = {d: zips(d) for d in dates}
    first_complete = next(
        d for d in dates if coverage[d] >= COMPLETE_SHARE * coverage[dates[-1]]
    )
    if first_complete > dates[0]:
        log.append(
            f"{abbr}: boundary records before {first_complete.date()} cover "
            f"{coverage[dates[0]]} ZIP codes on {dates[0].date()} against "
            f"{coverage[first_complete]} on {first_complete.date()}; earlier "
            f"dates use the {first_complete.date()} boundaries"
        )
    out = []
    for d in dates:
        when = max(d, first_complete)
        b = boundary[(boundary.begin <= when) & (boundary.end >= when)]
        lookup = rate_lookup(rates, d)
        # Codes whose rate row has another type than the boundary lists.
        by_code: dict = {}
        for (t, c), r in lookup.items():
            by_code.setdefault(c, set()).add(r)
        state_rate = lookup[("45", state_fips)]
        combined = np.where(b.state_indicator == state_fips, state_rate, 0.0)
        combined = combined + np.array(
            [lookup.get(("00", c[2:]), 0.0) for c in b.county]
        )
        combined = combined + np.array(
            [lookup.get(("01", p), 0.0) if p else 0.0 for p in b.place]
        )
        by_type_code = {f"{t}|{c}": r for (t, c), r in lookup.items()}
        by_unique_code = {c: next(iter(v)) for c, v in by_code.items() if len(v) == 1}
        missing = set()
        for code, kind in SPECIALS:
            listed = b[code] != ""
            if not listed.any():
                continue
            value = (b[kind] + "|" + b[code]).map(by_type_code)
            # A code whose rate row carries another jurisdiction type.
            value = value.fillna(b[code].map(by_unique_code))
            unrated = listed & value.isna()
            missing |= set(zip(b[kind][unrated], b[code][unrated]))
            # A listed district with no rate in effect has no tax then.
            combined = combined + value.where(listed, 0.0).fillna(0.0).to_numpy()
        if missing:
            log.append(
                f"{abbr} {d.date()}: {len(missing)} special district codes "
                f"with no rate in effect, counted as 0: {sorted(missing)[:4]}"
            )
        frame = pd.DataFrame(
            {
                "county": b.county.to_numpy(),
                "code": b.place.to_numpy(),
                "priority": b.rtype.map(RECORD_TYPE_PRIORITY).to_numpy(),
                "rate": combined,
                "records": b.records.to_numpy(),
            }
        )
        finest = frame.groupby(["county", "code"]).priority.transform("min")
        frame = frame[frame.priority == finest]
        weighted = (
            (frame.rate * frame.records).groupby([frame.county, frame.code]).sum()
        )
        records = frame.groupby(["county", "code"]).records.sum()
        units = (weighted / records).rename("rate").to_frame()
        units["records"] = records
        units = units.reset_index()
        units["date"] = d
        out.append(units)
    return pd.concat(out, ignore_index=True)


def change_dates(dates: list[pd.Timestamp], tables: list[pd.DataFrame]) -> list:
    """The evaluation dates plus every date in the window on which a row of
    the tables begins or the day after one ends."""
    changes = set(dates)
    for table in tables:
        for column, shift in (("begin", 0), ("end", 1)):
            when = pd.to_datetime(table[column].unique()) + pd.Timedelta(days=shift)
            changes |= {d for d in when if dates[0] < d <= WINDOW_END}
    return sorted(changes)


# --- New York and Virginia ---------------------------------------------------


def pdf_text(path: Path) -> str:
    return subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def ny_unit_rates(sources: Path, dates: list[pd.Timestamp], log: list) -> pd.DataFrame:
    """New York counties and cities from the Publication 718 transcription,
    each reporting code and rate checked against the publication's text."""
    table = pd.read_csv(
        HERE / "ny_pub718.csv",
        dtype={"county_fips": str, "place_fips": str, "reporting_code": str},
        keep_default_na=False,
    )
    text = pdf_text(sources / "ny" / "pub718.pdf")
    fractions = {0: "", 0.125: "⅛", 0.25: "¼", 0.375: "⅜", 0.5: "½",
                 0.625: "⅝", 0.75: "¾", 0.875: "⅞"}  # fmt: skip
    current = table.sort_values("effective_from").drop_duplicates(
        ["county_fips", "place_fips"], keep="last"
    )
    for code, rate in zip(current.reporting_code, current.rate_percent):
        printed = f"{int(rate)}{fractions[rate - int(rate)]}"
        assert re.search(rf"\s{re.escape(printed)}\s+{code}\b", text), (
            f"Publication 718 does not print rate {printed} with code {code}"
        )
    table["effective_from"] = pd.to_datetime(table.effective_from)
    out = []
    for d in sorted(set(dates) | set(table.effective_from)):
        active = table[table.effective_from <= d].sort_values("effective_from")
        active = active.drop_duplicates(["county_fips", "place_fips"], keep="last")
        out.append(
            pd.DataFrame(
                {
                    "county": active.county_fips.to_numpy(),
                    "code": active.place_fips.to_numpy(),
                    "rate": active.rate_percent.to_numpy() / 100,
                    "records": 1,
                    "date": d,
                }
            )
        )
    return pd.concat(out, ignore_index=True)


def va_unit_rates(sources: Path, dates: list[pd.Timestamp], log: list) -> pd.DataFrame:
    """Virginia counties and independent cities from the Virginia Tax
    workbook: one sheet per period, the period's first day in the sheet's
    second row, and each locality's "General Sales" rate."""
    sheets = pd.read_excel(
        sources / "va" / VA_URL.rsplit("/", 1)[-1], sheet_name=None, header=None
    )
    periods = []
    for sheet in sheets.values():
        title = str(sheet.iloc[1, 1]).strip()
        start = pd.to_datetime(re.split(r"\s+-\s+", title)[0], format="mixed")
        body = sheet.iloc[4:].copy()
        body.columns = [str(h).strip() for h in sheet.iloc[3].tolist()]
        body = body[pd.to_numeric(body["Code"], errors="coerce").notna()]
        periods.append(
            pd.DataFrame(
                {
                    "county": body["Code"].astype(int).astype(str).str.zfill(5),
                    "rate": body["General Sales"].astype(float).round(6),
                    "start": start,
                }
            )
        )
    periods = pd.concat(periods, ignore_index=True)
    assert (periods.county.str[:2] == "51").all()
    out = []
    starts = {d for d in periods.start if dates[0] < d <= WINDOW_END}
    for d in sorted(set(dates) | starts):
        active = periods[periods.start <= d].sort_values("start")
        active = active.drop_duplicates("county", keep="last")
        out.append(
            pd.DataFrame(
                {
                    "county": active.county.to_numpy(),
                    "code": "",
                    "rate": active.rate.to_numpy(),
                    "records": 1,
                    "date": d,
                }
            )
        )
    return pd.concat(out, ignore_index=True)


# --- Census blocks and aggregation -------------------------------------------


def census_blocks(sources: Path, abbr: str) -> pd.DataFrame:
    """2020 Census tabulation blocks (summary level 750) with their county,
    county subdivision, place and population (POP100), from the P.L. 94-171
    geographic header file."""
    path = sources / "census" / "pl" / f"{abbr.lower()}2020.pl.zip"
    rows = []
    with zipfile.ZipFile(path) as archive:
        name = next(n for n in archive.namelist() if n.endswith("geo2020.pl"))
        with archive.open(name) as f:
            for line in io.TextIOWrapper(f, encoding="latin-1"):
                fields = line.rstrip("\n").split("|")
                if fields[2] != "750":
                    continue
                rows.append(
                    (
                        fields[12] + fields[14],
                        fields[17],
                        "" if fields[29] == "99999" else fields[29],
                        int(fields[90]),
                    )
                )
    return pd.DataFrame(rows, columns=["county", "cousub", "place", "population"])


def place_rates(
    abbr: str, blocks: pd.DataFrame, units: pd.DataFrame, log: list
) -> pd.DataFrame:
    """Population-weighted rate of each county's places and of its area
    outside every place (place ""), at each date.

    A block's taxing unit is its place's unit, else its county
    subdivision's (Vermont's local option taxes are levied by towns), else
    its county's unit without a place code. Units are matched within the
    block's county, or statewide when the state's boundary file carries no
    county codes (county ""). A block in none of these takes the
    record-weighted mean of its county's units, else of the state's.
    """
    out = []
    for d, at_date in units.groupby("date"):
        rate = {
            (c, u): r for c, u, r in zip(at_date.county, at_date.code, at_date.rate)
        }
        weighted = (at_date.rate * at_date.records).groupby(at_date.county).sum()
        county_mean = (weighted / at_date.groupby("county").records.sum()).to_dict()
        state_mean = float(
            (at_date.rate * at_date.records).sum() / at_date.records.sum()
        )

        def unit_rate(c: str, s: str, p: str) -> float:
            candidates = ([(c, p), ("", p)] if p else []) + [
                (c, s),
                ("", s),
                (c, ""),
                ("", ""),
            ]
            for key in candidates:
                if key in rate:
                    return rate[key]
            return county_mean.get(c, state_mean)

        block_rate = np.array(
            [
                unit_rate(c, s, p)
                for c, s, p in zip(blocks.county, blocks.cousub, blocks.place)
            ]
        )
        missing = np.isnan(block_rate)
        if missing.any():
            log.append(
                f"{abbr} {d.date()}: {int(blocks.population[missing].sum())} "
                f"people in counties without official rates: "
                f"{sorted(blocks.county[missing].unique())[:10]}"
            )
        b = blocks[~missing].assign(rate=block_rate[~missing])
        keys = [b.county, b.place]
        population = b.population.groupby(keys).sum()
        mean = (b.rate * b.population).groupby(keys).sum() / population
        # A place without residents takes the unweighted mean of its blocks.
        mean = mean.where(population > 0, b.rate.groupby(keys).mean())
        frame = pd.DataFrame({"rate": mean, "population": population})
        frame.index.names = ["county_fips", "place_fips"]
        frame = frame.reset_index()
        frame["effective_from"] = d
        out.append(frame)
    return pd.concat(out, ignore_index=True)


def assemble(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Drop places whose rate equals the rate outside every place in their
    county at every date, since a household in one takes that rate anyway;
    fold their populations into the county's remainder; and keep each key's
    first row and the rows where its rate changes."""
    table = table.copy()
    table["rate"] = table.rate.round(6)
    outside = (
        table[table.place_fips == ""].set_index(["county_fips", "effective_from"]).rate
    )
    outside_rate = pd.Series(
        list(zip(table.county_fips, table.effective_from)), index=table.index
    ).map(outside)
    differs = (table.rate != outside_rate) & (table.place_fips != "")
    keep_place = differs.groupby([table.county_fips, table.place_fips]).transform("any")
    kept = table[(table.place_fips == "") | keep_place]
    # Populations do not change with the date: take each key's last row.
    last = table.sort_values("effective_from").drop_duplicates(
        ["county_fips", "place_fips"], keep="last"
    )
    county_population = last.groupby("county_fips").population.sum()
    kept_last = last[(last.place_fips == "") | keep_place.reindex(last.index)]
    places = kept_last[kept_last.place_fips != ""][
        ["county_fips", "place_fips", "population"]
    ]
    remainder = county_population - places.groupby(
        "county_fips"
    ).population.sum().reindex(county_population.index, fill_value=0)
    populations = pd.concat(
        [
            places,
            pd.DataFrame(
                {
                    "county_fips": remainder.index,
                    "place_fips": "",
                    "population": remainder.to_numpy(),
                }
            ),
        ]
    ).sort_values(["county_fips", "place_fips"])
    # A county wholly inside places has no remainder row.
    populations = populations[
        (populations.place_fips != "")
        | (populations.population > 0)
        | populations.county_fips.isin(kept[kept.place_fips == ""].county_fips)
    ]
    kept = kept.sort_values(["county_fips", "place_fips", "effective_from"])
    previous = kept.groupby(["county_fips", "place_fips"]).rate.shift()
    kept = kept[previous.isna() | (previous != kept.rate)]
    return kept, populations


def build(sources: Path, only: list[str] | None = None) -> None:
    dates = evaluation_dates()
    log: list[str] = []
    tables = []
    states = [s for s in SST_STATES if s not in NO_LOCAL_TAX] + ["NY", "VA"]
    if only:
        states = [s for s in states if s in only]
    for abbr in states:
        print(f"{abbr}...", flush=True)
        if abbr == "NY":
            units = ny_unit_rates(sources, dates, log)
        elif abbr == "VA":
            units = va_unit_rates(sources, dates, log)
        else:
            units = sst_unit_rates(sources, abbr, dates, log)
        by_place = place_rates(abbr, census_blocks(sources, abbr), units, log)
        by_place["state_code"] = abbr
        tables.append(by_place)
    rates, populations = assemble(pd.concat(tables, ignore_index=True))
    rates["effective_from"] = rates.effective_from.dt.strftime("%Y-%m-%d")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rates[["state_code", "county_fips", "place_fips", "effective_from", "rate"]].to_csv(
        OUTPUT / "rates.csv", index=False, float_format="%.6f"
    )
    populations.to_csv(OUTPUT / "populations.csv", index=False)
    retrieved = sources / "retrieved_at.txt"
    manifest = {
        "retrieved_at": retrieved.read_text().strip() if retrieved.exists() else None,
        "sha256": {
            str(p.relative_to(sources)): sha256(p)
            for p in sorted(sources.rglob("*"))
            if p.is_file()
            and p.suffix.lower() in {".zip", ".csv", ".pdf", ".xlsx"}
            and p.relative_to(sources).parts[0] in {"sst", "ny", "va", "census"}
            and "x" not in p.relative_to(sources).parts
        },
        "log": log,
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print("\n".join(log))
    print(f"{len(rates)} rate rows, {len(populations)} population rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    parser.add_argument(
        "--states", nargs="*", help="Build only these states (for checking)."
    )
    args = parser.parse_args()
    if args.download:
        download(args.sources)
    build(args.sources, args.states)
