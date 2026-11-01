"""A researcher's flat file can move from state to state.

A simulated instrument runs the same people through each state's rules: read a
file, set ``state_fips``, build a dataset, run a simulation. ``state_fips`` has to
decide the state however much other geography the file still holds. Each test
here reads the file from a CSV, as a researcher would.
"""

import io
import logging

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
import numpy as np
import pandas as pd
import pytest
from policyengine_core.data import Dataset
from policyengine_core.errors import ParameterNotFoundError
from spm_calculator.errors import SPMInputError

from policyengine_us import Microsimulation
from policyengine_us.tools.geography.state_assignment import (
    STATE_CODE_BY_FIPS,
)

YEAR = 2024
NATIONAL_SPM = {"geography_kind": "national"}
MISSISSIPPI = 28
LOS_ANGELES_COUNTY = "06037"

SURVEY = """person_id,household_id,tax_unit_id,spm_unit_id,family_id,marital_unit_id,age,employment_income,household_weight
1,1,1,1,1,1,35,20000,1000
2,1,1,1,1,1,5,0,1000
3,2,2,2,2,2,41,45000,500
4,2,2,2,2,2,39,10000,500
5,2,2,2,2,4,12,0,500
6,2,2,2,2,5,9,0,500
7,3,3,3,3,6,67,12000,2000
"""


def read_survey(tmp_path):
    path = tmp_path / "your_survey.csv"
    path.write_text(SURVEY)
    return pd.read_csv(path)


def simulate(people, **kwargs):
    return Microsimulation(dataset=Dataset.from_dataframe(people, YEAR), **kwargs)


def with_state(people, fips):
    people = people.copy()
    people[f"state_fips__{YEAR}"] = fips
    return people


def state_warnings(caplog):
    return [
        record.getMessage()
        for record in caplog.records
        if record.levelno == logging.WARNING and "state_fips" in record.getMessage()
    ]


@pytest.mark.parametrize("fips", [6, 27, 28, 24, 50, 55])
def test_the_loop_runs_a_flat_file_through_a_state(tmp_path, fips):
    people = read_survey(tmp_path)
    people[f"state_fips__{YEAR}"] = fips
    simulation = Microsimulation(dataset=Dataset.from_dataframe(people, YEAR))

    assert set(simulation.calculate("state_code", YEAR).values) == {
        STATE_CODE_BY_FIPS[fips]
    }
    snap = simulation.calculate("is_snap_eligible", f"{YEAR}-01")
    assert len(snap) == 3
    assert snap.dtype == bool


def test_rules_differ_across_states_on_the_same_file(tmp_path):
    people = read_survey(tmp_path)
    tax = {
        fips: simulate(with_state(people, fips)).calculate("state_income_tax", YEAR)
        for fips in (6, 28)
    }
    assert not np.array_equal(tax[6].values, tax[28].values)


def test_a_state_swap_equals_dropping_the_finer_geography_by_hand(tmp_path):
    people = read_survey(tmp_path)
    kept = with_state(people, MISSISSIPPI)
    kept[f"county_fips__{YEAR}"] = LOS_ANGELES_COUNTY
    kept[f"zip_code__{YEAR}"] = "90001"
    kept[f"congressional_district_geoid__{YEAR}"] = 634
    dropped = with_state(people, MISSISSIPPI)

    for variable, period in [
        ("household_net_income", YEAR),
        ("state_income_tax", YEAR),
        ("is_snap_eligible", f"{YEAR}-01"),
        ("is_medicaid_eligible", YEAR),
    ]:
        assert np.array_equal(
            simulate(kept, spm=NATIONAL_SPM).calculate(variable, period).values,
            simulate(dropped, spm=NATIONAL_SPM).calculate(variable, period).values,
        ), variable


def test_a_county_keyed_parameter_survives_a_state_swap(tmp_path):
    people = with_state(read_survey(tmp_path), 27)
    people[f"county_fips__{YEAR}"] = LOS_ANGELES_COUNTY

    simulation = simulate(people)

    assert set(simulation.calculate("county", YEAR).values) == {"AITKIN_COUNTY_MN"}
    try:
        simulation.calculate("mn_ccap_provider_rate", f"{YEAR}-01")
    except ParameterNotFoundError as error:  # pragma: no cover
        pytest.fail(f"The stale county reached a Minnesota lookup: {error}")


def test_spm_county_thresholds_say_what_to_do_after_a_state_swap(tmp_path, caplog):
    people = with_state(read_survey(tmp_path), MISSISSIPPI)
    people[f"county_fips__{YEAR}"] = LOS_ANGELES_COUNTY

    with caplog.at_level(logging.WARNING):
        simulation = simulate(people)

    assert any(
        '"geography_kind": "national"' in text for text in state_warnings(caplog)
    )
    with pytest.raises(SPMInputError, match="geography_kind"):
        simulation.calculate("spm_unit_spm_threshold", YEAR)


def test_national_spm_thresholds_do_not_depend_on_the_state(tmp_path):
    people = read_survey(tmp_path)
    thresholds = [
        simulate(with_state(people, fips), spm=NATIONAL_SPM)
        .calculate("spm_unit_spm_threshold", YEAR)
        .values
        for fips in (6, MISSISSIPPI)
    ]
    assert np.array_equal(*thresholds)


@pytest.mark.parametrize(
    "label, value",
    [("state_code", "CA"), ("state_code_str", "CA"), ("state_name", "CA")],
)
def test_state_fips_outranks_a_stored_state_label(tmp_path, caplog, label, value):
    people = with_state(read_survey(tmp_path), MISSISSIPPI)
    people[f"{label}__{YEAR}"] = value

    with caplog.at_level(logging.WARNING):
        simulation = simulate(people)

    assert set(simulation.calculate("state_code", YEAR).values) == {"MS"}
    assert set(simulation.calculate("state_name", YEAR).values) == {"MS"}
    assert any("disagreed with state_fips" in text for text in state_warnings(caplog))


def test_geography_inside_the_state_stays_and_stays_quiet(tmp_path, caplog):
    people = with_state(read_survey(tmp_path), 6)
    people[f"county_fips__{YEAR}"] = LOS_ANGELES_COUNTY
    people[f"zip_code__{YEAR}"] = "90001"
    people[f"state_code__{YEAR}"] = "CA"

    with caplog.at_level(logging.WARNING):
        simulation = simulate(people)

    assert not state_warnings(caplog)
    assert set(simulation.calculate("county", YEAR).values) == {"LOS_ANGELES_COUNTY_CA"}
    assert set(simulation.calculate("zip_code", YEAR).values) == {"90001"}
    # Thresholds still read the county, because nothing contradicts it.
    assert simulation.calculate("spm_unit_spm_threshold", YEAR).sum() > 0


def test_values_derived_from_a_stale_county_leave_with_it(tmp_path):
    people = with_state(read_survey(tmp_path), MISSISSIPPI)
    people[f"county_fips__{YEAR}"] = "36061"
    people[f"in_nyc__{YEAR}"] = True
    people[f"three_digit_zip_code__{YEAR}"] = "100"
    people[f"medicaid_rating_area__{YEAR}"] = 4

    simulation = simulate(people)

    assert not simulation.calculate("in_nyc", YEAR).any()
    assert set(simulation.calculate("three_digit_zip_code", YEAR).values) == {""}
    assert set(simulation.calculate("medicaid_rating_area", YEAR).values) == {0}


def test_only_households_outside_the_state_lose_their_geography(tmp_path):
    people = read_survey(tmp_path)
    people[f"state_fips__{YEAR}"] = people["household_id"].map({1: 6, 2: 6, 3: 28})
    people[f"county_fips__{YEAR}"] = LOS_ANGELES_COUNTY
    people[f"zip_code__{YEAR}"] = "90001"

    simulation = simulate(people)

    assert simulation.calculate("county_fips", YEAR).values.tolist() == [
        LOS_ANGELES_COUNTY,
        LOS_ANGELES_COUNTY,
        "",
    ]
    assert simulation.calculate("zip_code", YEAR).values.tolist() == [
        "90001",
        "90001",
        "UNKNOWN",
    ]
    assert simulation.calculate("county", YEAR).values.tolist() == [
        "LOS_ANGELES_COUNTY_CA",
        "LOS_ANGELES_COUNTY_CA",
        "ADAMS_COUNTY_MS",
    ]


@pytest.mark.parametrize(
    "column, value",
    [
        ("county", "LOS_ANGELES_COUNTY_CA"),
        ("county_str", "LOS_ANGELES_COUNTY_CA"),
        ("tract_geoid", "06037101110"),
        ("block_geoid", "060371011101000"),
        ("congressional_district_geoid", 634),
    ],
)
def test_each_column_that_names_a_state_can_contradict_it(
    tmp_path, caplog, column, value
):
    people = with_state(read_survey(tmp_path), MISSISSIPPI)
    people[f"{column}__{YEAR}"] = value

    with caplog.at_level(logging.WARNING):
        simulation = simulate(people)

    assert any(column in text for text in state_warnings(caplog))
    assert set(simulation.calculate("county", YEAR).values) == {"ADAMS_COUNTY_MS"}


def test_a_reform_runs_both_arms_in_the_state(tmp_path):
    people = with_state(read_survey(tmp_path), MISSISSIPPI)
    people[f"county_fips__{YEAR}"] = LOS_ANGELES_COUNTY
    reform = {"gov.irs.credits.ctc.amount.base[0].amount": {"2024-01-01": 3000}}

    simulation = simulate(people, reform=reform, spm=NATIONAL_SPM)

    for arm in (simulation, simulation.baseline):
        assert set(arm.calculate("county", YEAR).values) == {"ADAMS_COUNTY_MS"}
        assert set(arm.calculate("state_code", YEAR).values) == {"MS"}


def test_a_later_year_keeps_the_state_a_file_set_once(tmp_path):
    simulation = simulate(with_state(read_survey(tmp_path), MISSISSIPPI))
    assert set(simulation.calculate("state_code", YEAR + 1).values) == {"MS"}


def test_one_year_of_a_multiyear_file_changing_gets_a_warning(tmp_path, caplog):
    people = with_state(read_survey(tmp_path), 6)
    people[f"state_fips__{YEAR + 1}"] = 6
    people[f"state_fips__{YEAR}"] = MISSISSIPPI

    with caplog.at_level(logging.WARNING):
        simulation = simulate(people)

    assert any("between" in text for text in state_warnings(caplog))
    assert set(simulation.calculate("state_code", YEAR).values) == {"MS"}
    assert set(simulation.calculate("state_code", YEAR + 1).values) == {"CA"}


def test_every_year_of_a_multiyear_file_changing_stays_quiet(tmp_path, caplog):
    people = with_state(read_survey(tmp_path), MISSISSIPPI)
    people[f"state_fips__{YEAR + 1}"] = MISSISSIPPI

    with caplog.at_level(logging.WARNING):
        simulate(people)

    assert not state_warnings(caplog)


def test_a_county_read_as_a_number_gets_a_warning(tmp_path, caplog):
    people = with_state(read_survey(tmp_path), 6)
    people[f"county_fips__{YEAR}"] = 6037

    with caplog.at_level(logging.WARNING):
        simulate(people)

    assert any("five-digit text" in record.getMessage() for record in caplog.records)


def test_a_state_that_does_not_exist_is_refused(tmp_path):
    with pytest.raises(ValueError, match="99"):
        simulate(with_state(read_survey(tmp_path), 99))


def test_a_flat_file_without_state_fips_keeps_the_default(tmp_path, caplog):
    with caplog.at_level(logging.WARNING):
        simulation = simulate(read_survey(tmp_path))
    assert not state_warnings(caplog)
    assert set(simulation.calculate("state_code", YEAR).values) == {"CA"}


def test_a_minor_only_unit_names_the_columns_that_fix_it(tmp_path):
    people = with_state(read_survey(tmp_path), 6)
    people.loc[people["household_id"] == 1, "age"] = 16

    simulation = simulate(people, spm=NATIONAL_SPM)

    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", YEAR)
    assert error.value.code == "SPM_COMPOSITION_REQUIRED"
    assert "__ETERNITY" in str(error.value)
    assert "is_spm_independent_minor_role" in str(error.value)
    assert str(error.value).count("is_spm_independent_minor_role") == 1


def test_a_household_head_column_clears_a_minor_only_unit(tmp_path):
    people = with_state(read_survey(tmp_path), 6)
    people.loc[people["household_id"] == 1, "age"] = 16
    people["is_household_head__ETERNITY"] = people["person_id"].isin([1, 3, 7])

    simulation = simulate(people, spm=NATIONAL_SPM)

    assert simulation.calculate("spm_unit_spm_threshold", YEAR).sum() > 0


def test_a_group_variable_of_text_maps_to_a_group_entity(tmp_path):
    simulation = simulate(with_state(read_survey(tmp_path), MISSISSIPPI))
    assert set(
        simulation.calculate("state_code_str", YEAR, map_to="spm_unit").values
    ) == {"MS"}


def test_an_export_reloads_with_the_same_answers(tmp_path):
    people = with_state(read_survey(tmp_path), MISSISSIPPI)
    first = simulate(people, spm=NATIONAL_SPM)
    export = first.to_input_dataframe(period=YEAR)
    buffer = io.StringIO()
    export.to_csv(buffer, index=False)
    buffer.seek(0)
    second = Microsimulation(
        dataset=Dataset.from_dataframe(pd.read_csv(buffer), YEAR),
        spm=NATIONAL_SPM,
    )

    for variable, period in [
        ("household_net_income", YEAR),
        ("is_snap_eligible", f"{YEAR}-01"),
    ]:
        assert np.array_equal(
            first.calculate(variable, period).values,
            second.calculate(variable, period).values,
        ), variable


def test_an_export_keeps_the_source_input_role(tmp_path):
    people = with_state(read_survey(tmp_path), 6)
    people.loc[people["household_id"] == 1, "age"] = 16
    people["is_spm_independent_minor_role__ETERNITY"] = people["person_id"] == 1

    export = simulate(people, spm=NATIONAL_SPM).to_input_dataframe(period=YEAR)

    assert "is_spm_independent_minor_role__ETERNITY" in export.columns


@settings(
    max_examples=12,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    fips=st.sampled_from(sorted(STATE_CODE_BY_FIPS)),
    stale=st.sampled_from(sorted(STATE_CODE_BY_FIPS)),
)
def test_state_fips_always_decides_the_state(tmp_path_factory, fips, stale):
    """For any pair of states, the stored county of one yields to the other."""
    people = with_state(read_survey(tmp_path_factory.mktemp("survey")), fips)
    people[f"county_fips__{YEAR}"] = f"{stale:02d}001"
    people[f"state_code__{YEAR}"] = STATE_CODE_BY_FIPS[stale]

    simulation = simulate(people)

    assert set(simulation.calculate("state_code", YEAR).values) == {
        STATE_CODE_BY_FIPS[fips]
    }
    county = set(simulation.calculate("county", YEAR).values)
    assert all(name.endswith(f"_{STATE_CODE_BY_FIPS[fips]}") for name in county)
