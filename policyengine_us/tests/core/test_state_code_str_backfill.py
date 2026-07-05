"""A situation that sets only ``state_code_str`` must resolve the ``state_code`` enum.

The geography variables derive one-directionally
(``state_fips`` -> ``state_name`` -> ``state_code`` -> ``state_code_str``), so a
situation that supplies only ``state_code_str`` used to feed no upstream reader:
every variable reading the ``state_code`` enum silently fell back to the default,
``StateCode.CA``, while ``state_code_str`` readers saw the intended state
(PolicyEngine/policyengine-us#8887).

The ``Simulation``/``Microsimulation`` wrappers now backfill ``state_code`` from
``state_code_str``, mirroring the ``employment_income`` ->
``employment_income_before_lsr`` moves. These tests exercise the Python wrapper
directly because the YAML runner builds simulations without the wrapper and so
cannot cover the backfill.
"""

import numpy as np
import pandas as pd

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset

YEAR = 2026


def _single_person_situation(geo_key: str | None = None, geo_value: str = "KS") -> dict:
    household = {"members": ["person"]}
    if geo_key is not None:
        household[geo_key] = {str(YEAR): geo_value}
    return {
        "people": {
            "person": {
                "age": {str(YEAR): 30},
                "employment_income": {str(YEAR): 20_000},
            }
        },
        "spm_units": {"spm_unit": {"members": ["person"]}},
        "tax_units": {"tax_unit": {"members": ["person"]}},
        "households": {"household": household},
    }


def test_state_code_str_only_resolves_state_code_enum():
    """state_code_str-only input must set the enum, not leave the CA default."""
    simulation = Simulation(situation=_single_person_situation("state_code_str", "KS"))

    assert simulation.calculate("state_code", YEAR).decode_to_str()[0] == "KS"
    assert simulation.calculate("state_code_str", YEAR)[0] == "KS"


def test_state_code_str_only_matches_state_code_enum_input():
    """The SUA/utility chain (a state_code-enum reader) must see the same state.

    ``snap_utility_region`` reads the ``state_code`` enum, so before the fix a
    ``state_code_str: KS`` household evaluated it under California's region.
    """
    via_str = Simulation(situation=_single_person_situation("state_code_str", "KS"))
    via_enum = Simulation(situation=_single_person_situation("state_code", "KS"))

    assert (
        via_str.calculate("snap_utility_region", YEAR)[0]
        == via_enum.calculate("snap_utility_region", YEAR)[0]
    )


def test_state_code_str_only_yields_that_states_income_tax_not_california():
    """A NY household sent via state_code_str owes NY tax, not California's."""
    ny_via_str = Simulation(
        situation=_single_person_situation("state_code_str", "NY")
    ).calculate("state_income_tax", YEAR)[0]
    ny_via_enum = Simulation(
        situation=_single_person_situation("state_code", "NY")
    ).calculate("state_income_tax", YEAR)[0]
    ca_via_enum = Simulation(
        situation=_single_person_situation("state_code", "CA")
    ).calculate("state_income_tax", YEAR)[0]

    # The string path now equals the enum path for the same state...
    assert ny_via_str == ny_via_enum
    # ...and is not the California default that the bug produced.
    assert ny_via_str != ca_via_enum


def test_no_geography_situation_defaults_to_california():
    """A situation with no geography input must keep the CA default."""
    simulation = Simulation(situation=_single_person_situation(geo_key=None))

    assert simulation.calculate("state_code", YEAR).decode_to_str()[0] == "CA"


def test_explicit_state_code_wins_over_state_code_str():
    """An explicitly set state_code enum is never overwritten by the backfill."""
    situation = _single_person_situation("state_code", "NY")
    situation["households"]["household"]["state_code_str"] = {str(YEAR): "KS"}

    simulation = Simulation(situation=situation)

    assert simulation.calculate("state_code", YEAR).decode_to_str()[0] == "NY"


def test_state_code_str_backfill_propagates_across_periods():
    """Like the income backfill, the geography backfill covers every set period."""
    situation = _single_person_situation("state_code_str", "NY")
    # Add a second period of geography (and the inputs it needs).
    situation["people"]["person"]["age"]["2025"] = 29
    situation["people"]["person"]["employment_income"]["2025"] = 18_000
    situation["households"]["household"]["state_code_str"]["2025"] = "NY"

    simulation = Simulation(situation=situation)

    assert simulation.calculate("state_code", 2025).decode_to_str()[0] == "NY"
    assert simulation.calculate("state_code", 2026).decode_to_str()[0] == "NY"


def _state_fips_dataset(state_fips: list[int]) -> USSingleYearDataset:
    n = len(state_fips)
    ids = np.arange(1, n + 1)
    person = pd.DataFrame(
        {
            "person_id": ids,
            "person_household_id": ids,
            "person_tax_unit_id": ids,
            "person_spm_unit_id": ids,
            "person_family_id": ids,
            "person_marital_unit_id": ids,
            "age": np.full(n, 40.0),
            "employment_income": np.full(n, 50_000.0),
        }
    )
    household = pd.DataFrame(
        {
            "household_id": ids,
            "state_fips": np.asarray(state_fips, dtype="int64"),
            "household_weight": np.full(n, 1.0),
        }
    )
    return USSingleYearDataset(
        person=person,
        household=household,
        tax_unit=pd.DataFrame({"tax_unit_id": ids}),
        spm_unit=pd.DataFrame({"spm_unit_id": ids}),
        family=pd.DataFrame({"family_id": ids}),
        marital_unit=pd.DataFrame({"marital_unit_id": ids}),
        time_period=2024,
    )


def test_microsimulation_state_fips_dataset_unaffected_by_backfill():
    """Datasets carry state_fips, so the backfill is a no-op for them.

    The chain state_fips -> state_name -> state_code -> state_code_str must still
    resolve per household (36 -> NY, 6 -> CA), not collapse to a single state.
    """
    simulation = Microsimulation(dataset=_state_fips_dataset([36, 6]))

    assert list(simulation.calculate("state_code_str", 2024)) == ["NY", "CA"]
