"""Parameter scales must not repeat a threshold at any instant.

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
"""

import math
from collections import defaultdict
from datetime import date

from policyengine_core.parameters import ParameterNode, ParameterScale
from policyengine_core.parameters.operations.uprate_parameters import (
    uprate_parameters,
)

from policyengine_us.system import system


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


def _all_scales():
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

    assert tied.count("2022-01-01") == 2
    assert _duplicate_threshold_errors(colliding) == [
        "root.table: brackets [0, 1] share threshold 300 at 2022-01-01"
    ]
    assert _duplicate_threshold_errors(distinct) == []


def _is_calendar_date(instant_str):
    # Core's public lookup parses the instant, which fails for padded
    # 0000-01-01 entries and for 2021-06-31 in
    # gov.states.ny.nyserda.drive_clean.amount.
    try:
        date.fromisoformat(instant_str)
    except ValueError:
        return False
    return True


def test_add_bracket_thresholds_match_core_for_every_scale_and_instant():
    mismatches = []
    for scale in _all_scales():
        for instant_str in _change_instants(scale):
            if not _is_calendar_date(instant_str):
                continue
            expected = sorted(
                {
                    float(threshold)
                    for _, threshold in _add_bracket_thresholds(scale, instant_str)
                }
            )
            actual = [float(threshold) for threshold in scale(instant_str).thresholds]
            if expected != actual:
                mismatches.append(f"{scale.name} at {instant_str}")

    assert not mismatches, "\n".join(mismatches)


def test_parameter_scales_have_no_duplicate_thresholds():
    scales = _all_scales()
    errors = [error for scale in scales for error in _duplicate_threshold_errors(scale)]

    assert scales
    assert not errors, "\n".join(errors)
