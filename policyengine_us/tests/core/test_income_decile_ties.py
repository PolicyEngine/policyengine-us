"""Invented person-weighted deciles under the shared upper-rank tie convention.

Python is needed for independently shuffled entity tables, unequal weights and
member counts, and count-gated nullable group summaries. No population file or
formula-owned dataset output is used. Both decile formulas remain unmodified.
"""

import socket

import h5py
import numpy as np
import pandas as pd
import pytest
import requests
from policyengine_core.reforms import Reform
from policyengine_core.variables import Variable

from policyengine_us import Microsimulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.spm import spm_universe_mask


YEAR = 2024
STATUS = "spm_unit_spm_universe_status"
EXPECTED_DECILES = {10: 1, 20: 7, 30: 7, 40: 10}
MEASURES = (
    pytest.param("household", "household_income_decile", id="household"),
    pytest.param("spm_unit", "spm_unit_income_decile", id="spm"),
)


@pytest.fixture(autouse=True)
def no_population_data_reads(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Decile tie tests cannot read population data or network")

    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(pd, "HDFStore", forbidden)
    monkeypatch.setattr(h5py, "File", forbidden)


def _invented_income(entity_ids):
    """Income labels attached to IDs, independent of source row order."""
    return np.select(
        [entity_ids == 10, entity_ids == 20, entity_ids == 30, entity_ids == 40],
        [50.0, 100.0, 100.0, 300.0],
        default=1_000_000_000.0,
    )


class household_net_income(Variable):
    def formula(household, period, parameters):
        return _invented_income(household("household_id", period))


class spm_unit_net_income(Variable):
    def formula(spm_unit, period, parameters):
        included = spm_universe_mask(spm_unit, period)
        equivalised_income = _invented_income(spm_unit("spm_unit_id", period))
        # The four-member unit receives resources 200 and the actual OECD
        # formula divides by sqrt(4), tying it with the one-member unit at 100.
        resources = equivalised_income * np.sqrt(spm_unit.nb_persons())
        return np.where(included, resources, np.nan)


class InventedResources(Reform):
    """Supply test resources through formulas, preserving dataset input guards."""

    def apply(self):
        self.update_variable(household_net_income)
        self.update_variable(spm_unit_net_income)


def invented_dataset(*, shuffled=False, include_outside=False):
    # ID, member count, household weight. The included person weights are
    # 1, 2, 4 and 3, totaling 10. Below the tie is weight1; the tie contributes
    # weight2+4, so BOTH tied units have upper cumulative rank7/10 -> decile7.
    # These are hand-specified fixture expectations, not aggregated model weights.
    units = [(10, 1, 1.0), (20, 1, 2.0), (30, 4, 1.0), (40, 1, 3.0)]
    if include_outside:
        units.append((50, 1, 1_000_000.0))
    people = []
    for identity, members, _ in units:
        for member in range(members):
            person_id = identity * 10 + member + 1
            people.append(
                {
                    "person_id": person_id,
                    "age": 40,
                    "is_household_head": member == 0,
                    "is_tax_unit_head": member == 0,
                    "person_marital_unit_id": person_id,
                    **{
                        f"person_{entity}_id": identity
                        for entity in ("household", "tax_unit", "family", "spm_unit")
                    },
                }
            )
    ids = [identity for identity, _, _ in units]
    tables = {
        "person": pd.DataFrame(people),
        "household": pd.DataFrame(
            {
                "household_id": ids,
                "household_weight": [weight for _, _, weight in units],
                "state_code": "CA",
                "county_fips": "06037",
            }
        ),
        "spm_unit": pd.DataFrame(
            {
                "spm_unit_id": ids,
                STATUS: [
                    "OUTSIDE" if identity == 50 else "INCLUDED" for identity in ids
                ],
            }
        ),
        "tax_unit": pd.DataFrame({"tax_unit_id": ids}),
        "family": pd.DataFrame({"family_id": ids}),
        "marital_unit": pd.DataFrame(
            {"marital_unit_id": [person["person_id"] for person in people]}
        ),
    }
    if shuffled:
        # Different permutations ensure IDs, not matching table positions, link
        # people and groups. Each permutation is deterministic.
        tables = {
            name: frame.sample(frac=1, random_state=17 + index).reset_index(drop=True)
            for index, (name, frame) in enumerate(tables.items())
        }
    return USSingleYearDataset(**tables, time_period=YEAR)


def simulate(**kwargs):
    return Microsimulation(dataset=invented_dataset(**kwargs), reform=InventedResources)


def deciles_by_id(simulation, entity, variable):
    ids = simulation.calc(f"{entity}_id", period=YEAR, map_to=entity)
    deciles = simulation.calc(variable, period=YEAR, map_to=entity)
    # Align scalar assertions by identity only; all weighted statistics below
    # remain MicroSeries operations on model-projected results.
    return {int(ids.iloc[index]): deciles.iloc[index] for index in range(len(ids))}


@pytest.mark.parametrize("entity,variable", MEASURES)
@pytest.mark.parametrize("shuffled", [False, True], ids=["ordered", "shuffled"])
def test_equal_incomes_share_the_upper_person_weighted_decile(
    entity, variable, shuffled
):
    simulation = simulate(shuffled=shuffled)
    assert deciles_by_id(simulation, entity, variable) == EXPECTED_DECILES
    ids = simulation.calc(f"person_{entity}_id", period=YEAR, map_to="person")
    deciles = simulation.calc(variable, period=YEAR, map_to="person")
    for index in range(len(ids)):
        assert deciles.iloc[index] == EXPECTED_DECILES[int(ids.iloc[index])]
    assert deciles.count() == 10
    # A household-count-weighted estimator would put the tie at ceil(4/7*10)=6;
    # ignoring survey weights would put it at ceil(6/7*10)=9. Neither is seven.
    assert (deciles == 7).sum() == 6


@pytest.mark.parametrize("entity,variable", MEASURES)
def test_independently_shuffled_tables_preserve_deciles_by_entity_id(entity, variable):
    ordered = simulate()
    shuffled = simulate(shuffled=True)
    assert deciles_by_id(ordered, entity, variable) == deciles_by_id(
        shuffled, entity, variable
    )


@pytest.mark.parametrize("shuffled", [False, True], ids=["ordered", "shuffled"])
def test_dominant_outside_weight_is_excluded_from_spm_tie_ranks(shuffled):
    simulation = simulate(shuffled=shuffled, include_outside=True)
    standalone = simulate(shuffled=shuffled)
    actual = deciles_by_id(simulation, "spm_unit", "spm_unit_income_decile")
    expected = deciles_by_id(standalone, "spm_unit", "spm_unit_income_decile")
    assert {identity: actual[identity] for identity in EXPECTED_DECILES} == expected
    assert expected == EXPECTED_DECILES
    assert pd.isna(actual[50])
    ranks = simulation.calc("spm_unit_income_decile", period=YEAR, map_to="person")
    assert ranks.count() == 10
    assert (ranks == 7).sum() == 6
    assert simulation.calc("age", period=YEAR, map_to="person").count() == 1_000_010


@pytest.mark.parametrize("entity,variable", MEASURES)
def test_empty_decile_groups_have_zero_counts_and_nullable_means(entity, variable):
    simulation = simulate()
    deciles = simulation.calc(variable, period=YEAR, map_to="person")
    income_variable = (
        "household_net_income"
        if entity == "household"
        else "spm_unit_oecd_equiv_net_income"
    )
    income = simulation.calc(income_variable, period=YEAR, map_to="person")
    expected_nonempty = {1: (1, 50), 7: (6, 100), 10: (3, 300)}
    for decile in range(1, 11):
        group = income[deciles == decile]
        count = group.count()
        mean = group.mean() if count > 0 else None
        if decile in expected_nonempty:
            expected_count, expected_mean = expected_nonempty[decile]
            assert count == expected_count
            assert mean == expected_mean
        else:
            assert count == 0
            assert mean is None
