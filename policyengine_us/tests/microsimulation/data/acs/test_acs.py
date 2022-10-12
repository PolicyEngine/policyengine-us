from policyengine_us.data import ACS
import pytest
from policyengine_us import Microsimulation

ACS_YEARS = []


@pytest.mark.dependency(name="acs")
@pytest.mark.parametrize("year", ACS_YEARS)
def test_acs_dataset_generates(year):
    ACS.generate(year)


@pytest.mark.dependency(depends=["acs"])
@pytest.mark.parametrize("year", ACS_YEARS)
def test_acs_policyengine_us_compatible(year):
    Microsimulation(dataset=ACS, year=year).calc("employment_income")
