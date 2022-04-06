from openfisca_us.microdata import ACS
import pytest
from openfisca_us import Microsimulation

ACS_YEARS = (2018,)


@pytest.mark.dependency(name="acs")
@pytest.mark.parametrize("year", ACS_YEARS)
def test_ACS_dataset_generates(year):
    ACS.generate(year)


@pytest.mark.dependency(depends=["acs"])
@pytest.mark.parametrize("year", ACS_YEARS)
def test_acs_openfisca_us_compatible(year):
    Microsimulation(dataset=ACS, year=year)
