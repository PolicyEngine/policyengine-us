import json
from importlib.resources import files

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


@pytest.fixture(scope="module")
def providers():
    catalog = files("policyengine_us").joinpath("data", "utility_providers.json")
    return json.loads(catalog.read_text(encoding="utf-8"))


@pytest.mark.parametrize("variable", [electricity_provider, natural_gas_provider])
def test_catalog_matches_model_choices(variable, providers):
    options = providers[variable.__name__]
    assert [(option["value"], option["label"]) for option in options] == [
        (choice.name, choice.value) for choice in variable.possible_values
    ]
    assert variable.default_value.name == "UNSPECIFIED"
    assert {option["value"] for option in options if option["states"] is None} == {
        "OTHER",
        "UNSPECIFIED",
    }
    for option in options:
        states = option["states"]
        if states is not None:
            assert states and set(states) <= StateCode.__members__.keys()
            assert len(states) == len(set(states))


def test_avista_territory_depends_on_fuel(providers):
    def avista_states(variable):
        return next(
            row["states"] for row in providers[variable] if row["value"] == "AVISTA"
        )

    assert set(avista_states("electricity_provider")) == {"ID", "MT", "WA"}
    assert set(avista_states("natural_gas_provider")) == {"ID", "OR", "WA"}
