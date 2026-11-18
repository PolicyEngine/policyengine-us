import pytest

from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)
from policyengine_us.variables.household.expense.utilities.electricity_provider import (
    electricity_provider,
)
from policyengine_us.variables.household.expense.utilities.natural_gas_provider import (
    natural_gas_provider,
)


@pytest.mark.parametrize("variable", [electricity_provider, natural_gas_provider])
def test_every_provider_has_a_territory(variable):
    territories = variable.metadata["states_by_value"]
    assert territories.keys() == {choice.name for choice in variable.possible_values}
    assert {key for key, value in territories.items() if value is None} == {
        "OTHER",
        "UNSPECIFIED",
    }
    for states in territories.values():
        if states is not None:
            assert states and set(states) <= StateCode.__members__.keys()
            assert len(states) == len(set(states))


def test_avista_territory_depends_on_fuel():
    assert set(electricity_provider.metadata["states_by_value"]["AVISTA"]) == {
        "ID",
        "MT",
        "WA",
    }
    assert set(natural_gas_provider.metadata["states_by_value"]["AVISTA"]) == {
        "ID",
        "OR",
        "WA",
    }
