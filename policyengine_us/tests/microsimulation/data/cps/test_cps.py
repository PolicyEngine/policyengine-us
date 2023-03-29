from policyengine_us.data import CPS_2021, CPS_2022, CPS_2023
import pytest
from policyengine_us import Microsimulation
import warnings

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

CPS_YEARS = []


@pytest.mark.dependency(name="cps")
@pytest.mark.parametrize("year", CPS_YEARS)
def test_cps_dataset_generates(year):
    year()


@pytest.mark.dependency(depends=["cps"])
@pytest.mark.parametrize("year", CPS_YEARS)
def test_cps_policyengine_us_compatible(year):
    Microsimulation(dataset=year).calc("employment_income")
