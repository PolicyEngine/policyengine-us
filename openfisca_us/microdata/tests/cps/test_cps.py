from openfisca_us.microdata import CPS, REPO
import pytest
import yaml
import pandas as pd
from itertools import product
from openfisca_us import Microsimulation

# Tolerance when comparing totals against taxcalc.
# We don't expect these to match since taxcalc uses its own weights.
MAX_REL_ERROR = 0.1
CPS_YEARS = (2020,)
ACS_YEARS = (2018,)
VARIABLES = (
    "e00200",
    "e00900",
    "e02400",
    "e02300",
    "e01500",
    "e00800",
)
with open(REPO.parent / "tests" / "cps" / "taxcalc_cps.yml", "r") as f:
    tc = yaml.safe_load(f)
sims = {}


@pytest.mark.dependency(name="cps")
@pytest.mark.parametrize("year", CPS_YEARS)
def test_CPS_dataset_generates(year):
    CPS.generate(year)


@pytest.mark.dependency(depends=["cps"])
@pytest.mark.parametrize("year", CPS_YEARS)
def test_cps_openfisca_us_compatible(year):
    Microsimulation(dataset=CPS, year=year).calc("tax")


@pytest.mark.dependency(depends=["cps"])
@pytest.mark.parametrize("year,variable", product(CPS_YEARS, VARIABLES))
def test_agg_against_taxcalc(year, variable):
    if year not in sims:
        sims[year] = Microsimulation(dataset=CPS, year=year)
    result = sims[year].calc(variable).sum()
    target = tc[variable][year]
    assert abs(result / target) < MAX_REL_ERROR


def _get_taxcalc_aggregates(
    cps_csv: str, cps_weights_csv: str
) -> pd.DataFrame:
    cps, weights = [
        pd.read_csv(file, compression="gzip")
        for file in (cps_csv, cps_weights_csv)
    ]
    aggregates = pd.DataFrame(
        {
            year: [
                (cps[column] * weights[f"WT{year}"]).sum() for column in cps
            ]
            for year in CPS_YEARS
        }
    )
    return aggregates
