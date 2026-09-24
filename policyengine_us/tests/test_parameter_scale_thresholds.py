"""Parameter scales must not repeat a finite threshold at any instant.

To build a scale at an instant, policyengine-core's
`ParameterScale._get_at_instant` passes every bracket to `add_bracket`,
which adds a bracket's amount (or rate) to an existing row with an equal
threshold instead of keeping a second row. Two brackets keyed to the same
threshold therefore collapse into one row that carries their sum, with no
error. The 2024 Arkansas low-income tax tables for head of household and
surviving spouse filers with two or more dependents shipped this way: the
$92 row was keyed at $24,200, the $104 row's threshold, so AGI of
$24,201-$24,300 got $196 and the $92 row disappeared.

Duplicate infinite thresholds are ignored: tables whose length changes over
time park unused brackets at `.inf`.
"""

import math
from collections import defaultdict

from policyengine_core.parameters import ParameterScale

from policyengine_us.system import system


def _value_at(parameter, instant_str):
    # Read the step function directly: some parameters carry padded
    # 0000-01-01 entries that policyengine-core cannot turn into a date.
    value = None
    for value_at_instant in sorted(
        parameter.values_list, key=lambda entry: entry.instant_str
    ):
        if value_at_instant.instant_str > instant_str:
            break
        value = value_at_instant.value
    return value


def _duplicate_threshold_errors(scale):
    thresholds = [bracket.children.get("threshold") for bracket in scale.brackets]
    instants = sorted(
        {
            value_at_instant.instant_str
            for threshold in thresholds
            if threshold is not None
            for value_at_instant in threshold.values_list
        }
    )
    errors = []
    for instant_str in instants:
        brackets_by_threshold = defaultdict(list)
        for index, threshold in enumerate(thresholds):
            if threshold is None:
                continue
            value = _value_at(threshold, instant_str)
            if value is None or math.isinf(value):
                continue
            brackets_by_threshold[float(value)].append(index)
        for value, indices in brackets_by_threshold.items():
            if len(indices) > 1:
                errors.append(
                    f"{scale.name} at {instant_str}: brackets {indices} "
                    f"share threshold {value:,.15g}"
                )
    return errors


def _scale(brackets):
    return ParameterScale(
        "test_scale",
        {"metadata": {"type": "single_amount"}, "brackets": brackets},
        "test_scale.yaml",
    )


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
        "test_scale at 2024-01-01: brackets [1, 2] share threshold 200"
    ]
    # The guard targets the silent sum policyengine-core produces.
    at_2024 = scale("2024-01-01")
    assert at_2024.thresholds == [0, 200]
    assert at_2024.amounts == [0, 3]


def test_duplicate_threshold_guard_ignores_infinite_thresholds():
    scale = _scale(
        [
            {"threshold": {"2021-01-01": 0}, "amount": {"2021-01-01": 0}},
            {"threshold": {"2021-01-01": math.inf}, "amount": {"2021-01-01": 1}},
            {"threshold": {"2021-01-01": math.inf}, "amount": {"2021-01-01": 2}},
        ]
    )

    assert _duplicate_threshold_errors(scale) == []


def test_parameter_scales_have_no_duplicate_finite_thresholds():
    scales = [
        node
        for node in system.parameters.get_descendants()
        if isinstance(node, ParameterScale)
    ]
    errors = [error for scale in scales for error in _duplicate_threshold_errors(scale)]

    assert scales
    assert errors == []
