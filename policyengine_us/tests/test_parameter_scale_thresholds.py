"""Check parameter dates, bracket thresholds and NaN values.

To build a scale at an instant, policyengine-core's
`ParameterScale._get_at_instant` passes brackets to `add_bracket`, which adds
a bracket's amount (or rate) to an existing row with an equal threshold
instead of keeping a second row. Two brackets keyed to the same threshold
therefore collapse into one row that carries their sum, with no error. The
2024 Arkansas low-income tax tables for head of household and surviving
spouse filers with two or more dependents shipped this way: the $92 row was
keyed at $24,200, the $104 row's threshold, so AGI of $24,201-$24,300 got
$196 and the $92 row disappeared.

Duplicate `+inf` thresholds are exempt: tables whose length changes over
time park unused brackets there, and no finite value reaches them. `-inf` is
a reachable bottom row, so duplicates there are flagged.

Federal-style rate schedules such as `gov.irs.income.bracket` are not scales:
their `thresholds` node maps bracket numbers 1..N to a value per filing status,
and `tax_at_main_rates` reads bracket i's threshold as its top. A repeated
threshold empties a bracket and an inverted one is clamped (#9084), so either
silently taxes a band at the wrong rate. Each filing status's thresholds must
therefore strictly increase at every instant, again exempting `+inf`.
`tax_at_main_rates` leaves income above a finite final threshold untaxed,
so the shipped ordinary income schedules must end at `+inf`.

YAML's `.nan` loads as a float in a scalar or nested value, and every
comparison with it is false, so no parameter value may hold NaN at any depth.
"""

import calendar
import math
import re
from collections import defaultdict
from datetime import date

import pytest
from hypothesis import example, given
from hypothesis import strategies as st
from policyengine_core.parameters import Parameter, ParameterNode, ParameterScale
from policyengine_core.parameters.operations.uprate_parameters import (
    uprate_parameters,
)
from policyengine_core.taxscales.amount_tax_scale_like import AmountTaxScaleLike
from policyengine_core.taxscales.rate_tax_scale_like import RateTaxScaleLike


@pytest.fixture(scope="module")
def system():
    from policyengine_us.system import system as us_system

    return us_system


def _add_bracket_thresholds(scale, instant_str):
    """(bracket index, threshold) for each bracket that
    `ParameterScale._get_at_instant` passes to `add_bracket` at the instant.

    Mirrors core: a bracket joins only when its threshold and its value child
    (chosen by scale type, as core chooses it) are both non-None at the
    instant. Values come from `Parameter._get_at_instant`, which takes the
    first `values_list` entry on or before the instant; calling it with the
    string directly also handles padded 0000-01-01 entries, which the public
    lookup cannot turn into a date.
    """
    present = [
        {
            name: value
            for name, child in bracket.children.items()
            if (value := child._get_at_instant(instant_str)) is not None
        }
        for bracket in scale.brackets
    ]
    if scale.metadata.get("type") == "single_amount" or any(
        "amount" in children for children in present
    ):
        value_key = "amount"
    elif any("average_rate" in children for children in present):
        value_key = "average_rate"
    else:
        value_key = "rate"
    return [
        (index, children["threshold"])
        for index, children in enumerate(present)
        if "threshold" in children and value_key in children
    ]


def _change_instants(scale):
    # A collision can start when a threshold changes or when a bracket's
    # amount or rate starts, so check every date any bracket child changes.
    return sorted(
        {
            value_at_instant.instant_str
            for bracket in scale.brackets
            for child in bracket.children.values()
            for value_at_instant in getattr(child, "values_list", [])
        }
    )


def _duplicate_threshold_errors(scale):
    instants_by_collision = defaultdict(list)
    for instant_str in _change_instants(scale):
        brackets_by_threshold = defaultdict(list)
        for index, threshold in _add_bracket_thresholds(scale, instant_str):
            if threshold != math.inf:
                brackets_by_threshold[float(threshold)].append(index)
        for threshold, indices in brackets_by_threshold.items():
            if len(indices) > 1:
                instants_by_collision[(tuple(indices), threshold)].append(instant_str)
    errors = []
    for (indices, threshold), instants in instants_by_collision.items():
        when = instants[0]
        if len(instants) > 1:
            when = f"{len(instants)} instants from {instants[0]} to {instants[-1]}"
        errors.append(
            f"{scale.name}: brackets {list(indices)} share threshold "
            f"{threshold:,.15g} at {when}"
        )
    return errors


def _scale(brackets):
    return ParameterScale(
        "test_scale",
        {"metadata": {"type": "single_amount"}, "brackets": brackets},
        "test_scale.yaml",
    )


def _all_scales(system):
    return [
        node
        for node in system.parameters.get_descendants()
        if isinstance(node, ParameterScale)
    ]


def test_duplicate_threshold_guard_flags_a_later_collision():
    scale = _scale(
        [
            {"threshold": {"2021-01-01": 0}, "amount": {"2021-01-01": 0}},
            {
                "threshold": {"2021-01-01": 100, "2024-01-01": 200},
                "amount": {"2021-01-01": 1},
            },
            {"threshold": {"2021-01-01": 200}, "amount": {"2021-01-01": 2}},
        ]
    )

    assert _duplicate_threshold_errors(scale) == [
        "test_scale: brackets [1, 2] share threshold 200 at 2024-01-01"
    ]


def test_duplicate_threshold_guard_ignores_only_positive_infinity():
    def scale_with_two_brackets_at(threshold):
        return _scale(
            [
                {"threshold": {"2021-01-01": threshold}, "amount": {"2021-01-01": 1}},
                {"threshold": {"2021-01-01": threshold}, "amount": {"2021-01-01": 2}},
            ]
        )

    assert _duplicate_threshold_errors(scale_with_two_brackets_at(math.inf)) == []
    assert _duplicate_threshold_errors(scale_with_two_brackets_at(-math.inf)) == [
        "test_scale: brackets [0, 1] share threshold -inf at 2021-01-01"
    ]


def test_duplicate_threshold_guard_skips_brackets_core_skips():
    # Core leaves out a bracket whose amount has not started yet, so the
    # shared threshold only collides once bracket 1's amount begins.
    scale = _scale(
        [
            {"threshold": {"2021-01-01": 100}, "amount": {"2021-01-01": 1}},
            {"threshold": {"2021-01-01": 100}, "amount": {"2024-01-01": 2}},
        ]
    )

    assert _duplicate_threshold_errors(scale) == [
        "test_scale: brackets [0, 1] share threshold 100 at 2024-01-01"
    ]


def _uprated_scale(other_threshold):
    # Uprating from start_instant writes a second 2022-01-01 entry after the
    # explicit one; core's lookup takes the explicit 300.
    root = ParameterNode(
        "root",
        data={
            "index": {"values": {"2021-01-01": 1, "2022-01-01": 2}},
            "table": {
                "metadata": {"type": "single_amount"},
                "brackets": [
                    {
                        "threshold": {
                            "values": {"2021-01-01": 100, "2022-01-01": 300},
                            "metadata": {
                                "uprating": {
                                    "parameter": "index",
                                    "start_instant": "2021-01-01",
                                }
                            },
                        },
                        "amount": {"2021-01-01": 10},
                    },
                    {
                        "threshold": {"2021-01-01": other_threshold},
                        "amount": {"2021-01-01": 20},
                    },
                ],
            },
        },
    )
    uprate_parameters(root)
    return root.table


def test_duplicate_threshold_guard_reads_tied_dates_like_core():
    colliding = _uprated_scale(300)
    distinct = _uprated_scale(200)
    tied = [
        entry.instant_str
        for entry in colliding.brackets[0].children["threshold"].values_list
    ]

    if tied.count("2022-01-01") != 2:
        pytest.skip("core's uprating no longer writes a tied 2022-01-01 entry")
    assert _duplicate_threshold_errors(colliding) == [
        "root.table: brackets [0, 1] share threshold 300 at 2022-01-01"
    ]
    assert _duplicate_threshold_errors(distinct) == []


# Several parameter files key a value at 0000-01-01 to mean "since the
# beginning of time" (see tests/code_health/test_uprating_placement.py). Python
# dates have no year zero, so it is the one instant that is not a calendar date.
YEAR_ZERO_SENTINEL = "0000-01-01"


def _is_calendar_date(instant_str):
    # Core compares instants as strings and its INSTANT_PATTERN checks only the
    # digit ranges, so an impossible day such as 2021-06-31 loads and sorts
    # without error while naming no date.
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", instant_str) is None:
        return False
    try:
        date.fromisoformat(instant_str)
    except ValueError:
        return False
    return True


def _non_calendar_instants(parameter):
    return [
        value_at_instant.instant_str
        for value_at_instant in parameter.values_list
        if value_at_instant.instant_str != YEAR_ZERO_SENTINEL
        and not _is_calendar_date(value_at_instant.instant_str)
    ]


def test_calendar_date_guard_flags_impossible_dates_only():
    parameter = Parameter(
        "test_parameter",
        {
            "values": {
                YEAR_ZERO_SENTINEL: 0,
                "2021-06-30": 1,
                "2021-06-31": 2,
                "2024-02-29": 3,
                "2025-02-29": 4,
                "2025-04-31": 5,
            }
        },
    )

    assert sorted(_non_calendar_instants(parameter)) == [
        "2021-06-31",
        "2025-02-29",
        "2025-04-31",
    ]
    # Forms core's INSTANT_PATTERN or date.fromisoformat accept that are not
    # full YYYY-MM-DD days.
    for instant_str in ["2021", "2021-06", "20210630", "2021-W26-3"]:
        assert not _is_calendar_date(instant_str)


@given(st.dates())
@example(date(2000, 2, 29))
@example(date(2024, 2, 29))
def test_calendar_date_guard_accepts_real_calendar_dates(calendar_date):
    assert _is_calendar_date(calendar_date.isoformat())


@given(
    year=st.integers(min_value=1, max_value=9999),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=31),
)
@example(year=2021, month=6, day=31)
@example(year=1900, month=2, day=29)
@example(year=2000, month=2, day=29)
def test_calendar_date_guard_matches_gregorian_month_lengths(year, month, day):
    instant_str = f"{year:04d}-{month:02d}-{day:02d}"
    # The Gregorian month-length oracle independently checks impossible days,
    # including century years that are leap years only when divisible by 400.
    assert _is_calendar_date(instant_str) == (
        day <= calendar.monthrange(year, month)[1]
    )


@given(st.dates())
@example(date(2021, 6, 30))
def test_calendar_date_guard_requires_full_calendar_form(calendar_date):
    canonical = calendar_date.isoformat()
    iso_year, iso_week, iso_day = calendar_date.isocalendar()
    alternatives = (
        canonical[:4],
        canonical[:7],
        canonical.replace("-", ""),
        f"{iso_year:04d}-W{iso_week:02d}-{iso_day}",
    )
    for instant_str in alternatives:
        assert not _is_calendar_date(instant_str)


@given(
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=31),
)
@example(month=1, day=1)
@example(month=1, day=2)
@example(month=2, day=29)
def test_calendar_date_guard_exempts_only_beginning_of_time(month, day):
    instant_str = f"0000-{month:02d}-{day:02d}"
    parameter = Parameter(
        "test_parameter",
        {"values": {YEAR_ZERO_SENTINEL: 0, instant_str: 1}},
    )
    # Year zero is not a calendar year; only the exact documented sentinel is
    # exempt when validating the parameter's loaded instants.
    expected = [] if instant_str == YEAR_ZERO_SENTINEL else [instant_str]
    assert _non_calendar_instants(parameter) == expected


def test_parameter_instants_are_calendar_dates(system):
    errors = [
        f"{parameter.name}: {instant_str}"
        for parameter in system.parameters.get_descendants()
        if isinstance(parameter, Parameter)
        for instant_str in _non_calendar_instants(parameter)
    ]

    assert not errors, "\n".join(errors)


def test_add_bracket_thresholds_match_core_for_every_scale_and_instant(
    monkeypatch, system
):
    # Record every threshold core passes to add_bracket, repeats included, and
    # compare that multiset with the guard's; comparing the built scale's
    # thresholds would hide exactly the repeats the guard exists to find.
    passed = []
    for scale_class in (AmountTaxScaleLike, RateTaxScaleLike):
        original = scale_class.add_bracket

        def recording_add_bracket(self, threshold, value, original=original):
            passed.append(float(threshold))
            return original(self, threshold, value)

        monkeypatch.setattr(scale_class, "add_bracket", recording_add_bracket)

    mismatches = []
    for scale in _all_scales(system):
        for instant_str in _change_instants(scale):
            if instant_str == YEAR_ZERO_SENTINEL:
                # Core's public lookup cannot parse year zero.
                continue
            passed.clear()
            scale(instant_str)
            expected = sorted(
                float(threshold)
                for _, threshold in _add_bracket_thresholds(scale, instant_str)
            )
            if expected != sorted(passed):
                mismatches.append(f"{scale.name} at {instant_str}")

    assert not mismatches, "\n".join(mismatches)


def test_parameter_scales_have_no_duplicate_thresholds(system):
    scales = _all_scales(system)
    errors = [error for scale in scales for error in _duplicate_threshold_errors(scale)]

    assert scales
    assert not errors, "\n".join(errors)


def _mapped_threshold_tables(system):
    # A rate schedule's `thresholds` node sits beside the `rates` node that
    # `tax_at_main_rates` reads with it, and maps bracket numbers 1..N.
    return [
        node.children["thresholds"]
        for node in system.parameters.get_descendants()
        if isinstance(node, ParameterNode)
        and "rates" in node.children
        and isinstance(node.children.get("thresholds"), ParameterNode)
        and node.children["thresholds"].children
        and sorted(node.children["thresholds"].children)
        == sorted(
            str(i) for i in range(1, len(node.children["thresholds"].children) + 1)
        )
    ]


def _mapped_threshold_errors(node):
    brackets = sorted(node.children, key=int)
    columns = defaultdict(dict)
    for bracket in brackets:
        child = node.children[bracket]
        if isinstance(child, ParameterNode):
            for column, leaf in child.children.items():
                columns[column][bracket] = leaf
        else:
            columns[None][bracket] = child
    instants_by_error = defaultdict(list)
    for column, leaves in columns.items():
        instants = sorted(
            {
                value_at_instant.instant_str
                for leaf in leaves.values()
                for value_at_instant in leaf.values_list
            }
        )
        for instant_str in instants:
            present = [
                (bracket, value)
                for bracket in brackets
                if bracket in leaves
                and (value := leaves[bracket]._get_at_instant(instant_str)) is not None
            ]
            for (lower, low), (upper, high) in zip(present, present[1:]):
                if not low < high and not low == high == math.inf:
                    instants_by_error[(column, lower, upper)].append(
                        (instant_str, low, high)
                    )
    errors = []
    for (column, lower, upper), cases in instants_by_error.items():
        instant_str, low, high = cases[0]
        when = instant_str
        if len(cases) > 1:
            when = (
                f"{instant_str} and {len(cases) - 1} later instants to {cases[-1][0]}"
            )
        name = node.name if column is None else f"{node.name}.*.{column}"
        errors.append(
            f"{name}: bracket {upper} threshold {high:,.15g} does not exceed "
            f"bracket {lower} threshold {low:,.15g} at {when}"
        )
    return errors


def _mapped_table(thresholds):
    return ParameterNode("root", data={"thresholds": thresholds}).thresholds


def test_mapped_threshold_guard_flags_repeats_and_inversions():
    table = _mapped_table(
        {
            1: {"SINGLE": {"2024-01-01": 100}, "JOINT": {"2024-01-01": 200}},
            2: {
                "SINGLE": {"2024-01-01": 100},
                "JOINT": {"2024-01-01": 400, "2025-01-01": 150},
            },
            3: {"SINGLE": {"2024-01-01": 300}, "JOINT": {"2024-01-01": 600}},
        }
    )

    assert _mapped_threshold_errors(table) == [
        "root.thresholds.*.SINGLE: bracket 2 threshold 100 does not exceed "
        "bracket 1 threshold 100 at 2024-01-01",
        "root.thresholds.*.JOINT: bracket 2 threshold 150 does not exceed "
        "bracket 1 threshold 200 at 2025-01-01",
    ]


def test_mapped_threshold_guard_flags_negative_infinity_repeats_and_nan():
    table = _mapped_table(
        {
            1: {"SINGLE": {"2024-01-01": -math.inf}, "JOINT": {"2024-01-01": 100}},
            2: {
                "SINGLE": {"2024-01-01": -math.inf},
                "JOINT": {"2024-01-01": math.nan},
            },
            3: {"SINGLE": {"2024-01-01": 300}, "JOINT": {"2024-01-01": 600}},
        }
    )

    assert _mapped_threshold_errors(table) == [
        "root.thresholds.*.SINGLE: bracket 2 threshold -inf does not exceed "
        "bracket 1 threshold -inf at 2024-01-01",
        "root.thresholds.*.JOINT: bracket 2 threshold nan does not exceed "
        "bracket 1 threshold 100 at 2024-01-01",
        "root.thresholds.*.JOINT: bracket 3 threshold 600 does not exceed "
        "bracket 2 threshold nan at 2024-01-01",
    ]


def test_mapped_threshold_guard_ignores_only_parked_positive_infinity():
    def table_with_top(top):
        return _mapped_table(
            {
                1: {"SINGLE": {"2024-01-01": 100}},
                2: {"SINGLE": {"2024-01-01": math.inf}},
                3: {"SINGLE": {"2024-01-01": top}},
            }
        )

    assert _mapped_threshold_errors(table_with_top(math.inf)) == []
    assert _mapped_threshold_errors(table_with_top(500)) == [
        "root.thresholds.*.SINGLE: bracket 3 threshold 500 does not exceed "
        "bracket 2 threshold inf at 2024-01-01"
    ]


def test_mapped_bracket_thresholds_strictly_increase(system):
    tables = _mapped_threshold_tables(system)
    errors = [error for table in tables for error in _mapped_threshold_errors(table)]

    assert {
        "gov.irs.income.bracket.thresholds",
        "gov.irs.capital_gains.thresholds",
    } <= {table.name for table in tables}
    assert not errors, "\n".join(errors)


@pytest.mark.parametrize(
    "name",
    [
        "gov.irs.income.bracket",
        "gov.contrib.additional_tax_bracket.bracket",
    ],
)
def test_shipped_income_bracket_top_thresholds_are_infinite(name, system):
    table = system.parameters.get_child(f"{name}.thresholds")
    brackets = sorted(table.children, key=int)
    assert brackets
    statuses = {
        status for bracket in brackets for status in table.children[bracket].children
    }
    assert statuses

    for status in sorted(statuses):
        leaves = [table.children[bracket].children[status] for bracket in brackets]
        instants = sorted(
            {
                value_at_instant.instant_str
                for leaf in leaves
                for value_at_instant in leaf.values_list
            }
        )
        checked = 0
        for instant_str in instants:
            values = [leaf._get_at_instant(instant_str) for leaf in leaves]
            if all(value is None for value in values):
                continue
            checked += 1
            assert values[-1] == math.inf, (
                f"{name}.thresholds.{brackets[-1]}.{status}: "
                f"top threshold {values[-1]} at {instant_str}"
            )
        assert checked, f"{name}: no active thresholds for {status}"


def _nan_paths(value, path=""):
    if isinstance(value, float) and math.isnan(value):
        yield path or "value"
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from _nan_paths(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _nan_paths(key, f"{path}.key[{key!r}]")
            yield from _nan_paths(item, f"{path}[{key!r}]")
    elif isinstance(value, (set, frozenset)):
        for item in sorted(value, key=repr):
            yield from _nan_paths(item, f"{path}{{{item!r}}}")


def _nan_values(parameter):
    return [
        f"{value_at_instant.instant_str} {path}"
        for value_at_instant in parameter.values_list
        for path in _nan_paths(value_at_instant.value)
    ]


def test_nan_guard_flags_nan_in_scalars_and_nested_containers():
    parameter = Parameter(
        "test_parameter",
        {
            "values": {
                "2023-01-01": [1.0, [2.0, 3.0], {4.0, 5.0}],
                "2024-01-01": [1.0, [2.0, math.nan]],
                "2025-01-01": math.nan,
                "2026-01-01": [math.nan],
                "2027-01-01": [{"nested": [math.nan], math.nan: 1.0}],
                "2028-01-01": [{math.nan}],
            }
        },
    )

    assert sorted(_nan_values(parameter)) == [
        "2024-01-01 [1][1]",
        "2025-01-01 value",
        "2026-01-01 [0]",
        "2027-01-01 [0].key[nan]",
        "2027-01-01 [0]['nested'][0]",
        "2028-01-01 [0]{nan}",
    ]


def test_parameter_values_are_not_nan(system):
    parameters = [
        parameter
        for parameter in system.parameters.get_descendants()
        if isinstance(parameter, Parameter)
    ]
    errors = [
        f"{parameter.name}: {error}"
        for parameter in parameters
        for error in _nan_values(parameter)
    ]

    assert parameters
    assert not errors, "\n".join(errors)
