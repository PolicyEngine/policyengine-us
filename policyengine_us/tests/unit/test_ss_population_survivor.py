"""Survivor population scope uses the shared basis without building a model."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from policyengine_us.tools.social_security.pia import FormulaPath, compute_pia
from policyengine_us.tools.social_security.population_survivor import (
    survivor_formula_path,
)


PERIOD = SimpleNamespace(start=date(2026, 1, 1))
DEFAULTS = {
    "worker_birth_year": 0,
    "death_year": 0,
    "authoritative_year": 0,
    "prior_disability_eligibility": -1,
    "same_year_death_before_62": -1,
    "worker_birth_date": "",
    "death_date": "",
    "basis_provenance": "",
    "ordinary_non_windex": False,
    "year_only_not_january_1": False,
}
COMPLETE_BASIS = {
    "worker_birth_year": 1970,
    "death_year": 2025,
    "prior_disability_eligibility": 0,
    "basis_provenance": "Supplied ordinary worker computation basis",
    "ordinary_non_windex": True,
    "year_only_not_january_1": True,
}


class PersonInputs:
    ids = ("survivor", "worker")

    def __init__(self, **values):
        self.values = {**DEFAULTS, **values}

    def __call__(self, name, period):
        assert period is PERIOD
        field = name.removeprefix("ss_calculator_")
        # The complete basis belongs to the recipient. The linked row has no
        # assertions: the adapter must not combine partial bases across people.
        return [self.values[field], DEFAULTS[field]]


def parameters(increase):
    return SimpleNamespace(
        gov=SimpleNamespace(
            contrib=SimpleNamespace(
                congress=SimpleNamespace(
                    s770=SimpleNamespace(
                        section_2=lambda when: SimpleNamespace(
                            recompute_pre2026_death_before_eligibility=increase
                        )
                    )
                )
            )
        )
    )


def resolve(values=None, *, increase=False, eligibility_year=2025, worker_index=1):
    return survivor_formula_path(
        PersonInputs(**(COMPLETE_BASIS if values is None else values)),
        PERIOD,
        parameters(increase),
        0,
        FormulaPath(s770=True),
        eligibility_year,
        worker_index,
    )


def test_custom_reform_without_s770_does_not_require_a_deceased_worker_basis():
    path = FormulaPath(factor_values=(".95", ".32", ".15"))
    actual, unsupported = survivor_formula_path(None, PERIOD, None, 0, path, 2025, None)
    assert actual is path
    assert not unsupported


@pytest.mark.parametrize(
    ("increase", "gain_per_first_bend"),
    [(False, Decimal(".05")), (True, Decimal(".1634"))],
)
def test_preeligibility_death_switch_changes_only_bend_increase(
    increase, gain_per_first_bend
):
    path, unsupported = resolve(increase=increase)
    assert not unsupported
    assert path.s770
    assert path.s770_increase_first_bend_point is increase
    baseline = compute_pia(5000, 2025, bend_points=(960, 5785), round_result=False)
    reform = compute_pia(
        5000,
        2025,
        path,
        2026,
        "retroactive",
        bend_points=(960, 5785),
        round_result=False,
    )
    assert reform - baseline == gain_per_first_bend * 960


def test_post2025_preeligibility_death_receives_both_increases_with_switch_off():
    path, unsupported = resolve(
        {**COMPLETE_BASIS, "death_year": 2026}, eligibility_year=2026
    )
    assert not unsupported
    assert path.s770 and path.s770_increase_first_bend_point


def test_death_after62_is_outside_the_preeligibility_switch():
    path, unsupported = resolve(
        {**COMPLETE_BASIS, "worker_birth_year": 1950}, eligibility_year=2012
    )
    assert not unsupported
    assert path.s770 and path.s770_increase_first_bend_point


def test_authoritative_prior_disability_basis_receives_both_increases():
    path, unsupported = resolve(
        {
            **COMPLETE_BASIS,
            "prior_disability_eligibility": 1,
            "authoritative_year": 2020,
        },
        eligibility_year=2020,
    )
    assert not unsupported
    assert path.s770 and path.s770_increase_first_bend_point


def test_exact_january1_birth_uses_previous_attainment_year():
    path, unsupported = resolve(
        {
            **COMPLETE_BASIS,
            "worker_birth_year": 1964,
            "worker_birth_date": "1964-01-01",
            "death_year": 2026,
            "death_date": "2026-01-01",
            "year_only_not_january_1": False,
        },
        eligibility_year=2025,
    )
    assert not unsupported
    assert path.s770_increase_first_bend_point


@pytest.mark.parametrize(
    "missing",
    [
        {"worker_birth_year": 0},
        {"death_year": 0},
        {"prior_disability_eligibility": -1},
        {"basis_provenance": ""},
        {"ordinary_non_windex": False},
        {"year_only_not_january_1": False},
        {"prior_disability_eligibility": 1, "authoritative_year": 0},
    ],
)
def test_unavailable_basis_is_flagged_without_inference(missing):
    path, unsupported = resolve({**COMPLETE_BASIS, **missing})
    assert unsupported
    assert path.s770 and path.s770_increase_first_bend_point


def test_completely_absent_basis_is_unmodeled():
    _, unsupported = resolve({})
    assert unsupported


def test_sameyear_death_without_dates_or_assertion_is_unmodeled():
    _, unsupported = resolve({**COMPLETE_BASIS, "worker_birth_year": 1963})
    assert unsupported


@pytest.mark.parametrize(("before62", "increase"), [(0, True), (1, False)])
def test_sameyear_explicit_assertion_resolves_the_shared_basis(before62, increase):
    path, unsupported = resolve(
        {
            **COMPLETE_BASIS,
            "worker_birth_year": 1963,
            "same_year_death_before_62": before62,
        }
    )
    assert not unsupported
    assert path.s770_increase_first_bend_point is increase


@pytest.mark.parametrize(
    "invalid",
    [
        {"worker_birth_year": -1},
        {"death_year": -1},
        {"authoritative_year": -1},
        {"prior_disability_eligibility": 2},
        {"same_year_death_before_62": 2},
        {"worker_birth_date": "invalid"},
        {"death_date": "2025-02-30"},
        {"worker_birth_date": "1971-01-02"},
        {"death_date": "2024-01-02"},
        {"worker_birth_year": 1990, "death_year": 1980},
        {"death_year": 2027},
    ],
)
def test_explicit_invalid_basis_is_rejected(invalid):
    with pytest.raises(ValueError):
        resolve({**COMPLETE_BASIS, **invalid})


def test_survivor_benchmark_must_match_supplied_linked_computation_year():
    with pytest.raises(ValueError, match="computation years disagree"):
        resolve(eligibility_year=2024)


@pytest.mark.parametrize("worker_index", [None, -1, 2])
def test_invalid_worker_link_is_rejected(worker_index):
    with pytest.raises(ValueError, match="existing person"):
        resolve(worker_index=worker_index)
