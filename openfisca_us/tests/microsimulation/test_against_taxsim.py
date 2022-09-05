import os
from openfisca_us.api.microsimulation import Microsimulation
from openfisca_us.data.datasets import CPS
from openfisca_us.tools.dev.taxsim.generate_taxsim_tests import TaxSim35
import numpy as np
import pytest
import pandas as pd
import platform

# Disable warnings
import warnings

warnings.filterwarnings("ignore")

STATES = ["MD", "MA", "NY", "WA"]
DISTANCE = 100
MINIMUM_PERCENT_CLOSE = 0.65

if os.name != "nt":

    @pytest.fixture(scope="module")
    def taxsim():
        taxsim = TaxSim35()

        yield taxsim.generate_from_microsimulation(
            CPS, 2022, None, True, False
        ).set_index("taxsim_taxsimid")

    @pytest.fixture(scope="module")
    def sim():
        yield Microsimulation()


@pytest.mark.skipif(os.name == "nt", reason="This test is not run on Windows")
def test_federal_tax_against_taxsim(sim, taxsim):
    if platform.system() == "Windows":
        warnings.warn("This test is not run on Windows")
        raise pytest.skip()
    tax = sim.calc("income_tax")
    tax.index = sim.calc("tax_unit_id").values
    comparison_df = pd.DataFrame(index=sim.calc("tax_unit_id").values)
    comparison_df["openfisca_us"] = tax
    comparison_df["taxsim"] = taxsim.taxsim_fiitax
    relative_distance = np.absolute(
        comparison_df.openfisca_us - comparison_df.taxsim
    )
    percent_close = (relative_distance < DISTANCE).mean()
    assert percent_close > MINIMUM_PERCENT_CLOSE


@pytest.mark.skipif(os.name == "nt", reason="This test is not run on Windows")
@pytest.mark.parametrize("state", STATES)
def test_state_income_tax_against_taxsim(state: str, sim, taxsim):
    in_state = sim.calc("tax_unit_state").values == state
    tax = sim.calc("state_income_tax")
    tax.index = sim.calc("tax_unit_id").values
    comparison_df = pd.DataFrame(
        dict(
            openfisca_us=tax,
            taxsim=taxsim.taxsim_siitax,
        ),
        index=sim.calc("tax_unit_id").values,
    )
    comparison_df = comparison_df[in_state]
    relative_distance = np.absolute(
        comparison_df.openfisca_us - comparison_df.taxsim
    )
    percent_close = (relative_distance < DISTANCE).mean()
    assert percent_close > MINIMUM_PERCENT_CLOSE
