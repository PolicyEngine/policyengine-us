from policyengine_us.data import CPS
import pytest
from policyengine_us import Microsimulation
import warnings

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

CPS_YEARS = [2020]


@pytest.mark.dependency(name="cps")
@pytest.mark.parametrize("year", CPS_YEARS)
def test_cps_dataset_generates(year):
    CPS.generate(year)


@pytest.mark.dependency(depends=["cps"])
@pytest.mark.parametrize("year", CPS_YEARS)
def test_cps_policyengine_us_compatible(year):
    Microsimulation(dataset=CPS, dataset_year=year).calc("employment_income")
