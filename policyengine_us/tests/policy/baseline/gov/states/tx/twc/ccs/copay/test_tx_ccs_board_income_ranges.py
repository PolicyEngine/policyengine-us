"""Board parent share of cost scales meet TWC's income ranges and stay ordered.

Before TX3C, Texas Workforce Boards set parent share of cost amounts for the
SMI income ranges TWC published each Board Contract Year (WD 24-23 Attachment
2 for BCY 2024; the BCY 2025 ranges WD 20-24 sent for October 1 to December 8,
2024). tx_ccs_board_copay rebuilds each range limit from the SMI in force that
month. The first check runs board_scale_amount over every SMI cell of both
tables, family sizes 2 to 15, on each side of each limit, so a change to the
SMI parameter, the size factor or the rounding that moves any limit by a
dollar fails here. The other checks read the Board parameter files: every
Board scale must rise with income, and every Board that applies its own scale
must have one.
"""

from pathlib import Path

import numpy as np
import pytest
import yaml

from policyengine_us.system import system
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.states.tx.twc.ccs.copay.tx_ccs_board_copay import (
    board_scale_amount,
)
from policyengine_us.variables.gov.states.tx.twc.ccs.tx_ccs_workforce_board_region import (
    TXCCSWorkforceBoardRegion,
)

PACKAGE = next(
    parent
    for parent in Path(__file__).resolve().parents
    if parent.name == "policyengine_us"
)
BOARD = PACKAGE / "parameters/gov/states/tx/twc/ccs/copay/board"

SHARES = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85]

# Upper limit of each SMI range (20%, 30%, ..., 85% SMI) by family size, as
# TWC printed them.
TWC_UPPER_LIMITS = {
    # WD 24-23 Attachment 2, effective October 1, 2023 to September 30, 2024.
    "2024-03": {
        2: [1071, 1606, 2141, 2677, 3212, 3747, 4015, 4282, 4550],
        3: [1323, 1984, 2645, 3306, 3968, 4629, 4959, 5290, 5621],
        4: [1574, 2362, 3149, 3936, 4723, 5511, 5904, 6298, 6691],
        5: [1826, 2740, 3653, 4566, 5479, 6392, 6849, 7305, 7762],
        6: [2078, 3117, 4157, 5196, 6235, 7274, 7793, 8313, 8833],
        7: [2125, 3188, 4251, 5314, 6376, 7439, 7971, 8502, 9033],
        8: [2173, 3259, 4345, 5432, 6518, 7605, 8148, 8691, 9234],
        9: [2220, 3330, 4440, 5550, 6660, 7770, 8325, 8880, 9435],
        10: [2267, 3401, 4534, 5668, 6802, 7935, 8502, 9069, 9636],
        11: [2314, 3472, 4629, 5786, 6943, 8100, 8679, 9258, 9836],
        12: [2362, 3542, 4723, 5904, 7085, 8266, 8856, 9447, 10037],
        13: [2409, 3613, 4818, 6022, 7227, 8431, 9033, 9636, 10238],
        14: [2456, 3684, 4912, 6140, 7368, 8596, 9210, 9824, 10438],
        15: [2503, 3755, 5007, 6258, 7510, 8762, 9388, 10013, 10639],
    },
    # BCY 2025 ranges, effective October 1 to December 8, 2024.
    "2024-11": {
        2: [1170, 1755, 2339, 2924, 3509, 4094, 4387, 4679, 4971],
        3: [1445, 2167, 2890, 3612, 4335, 5057, 5419, 5780, 6141],
        4: [1720, 2580, 3440, 4301, 5161, 6021, 6451, 6881, 7311],
        5: [1995, 2993, 3991, 4989, 5986, 6984, 7483, 7982, 8481],
        6: [2271, 3406, 4541, 5677, 6812, 7947, 8515, 9083, 9650],
        7: [2322, 3483, 4645, 5806, 6967, 8128, 8709, 9289, 9870],
        8: [2374, 3561, 4748, 5935, 7122, 8309, 8902, 9496, 10089],
        9: [2426, 3638, 4851, 6064, 7277, 8489, 9096, 9702, 10308],
        10: [2477, 3716, 4954, 6193, 7431, 8670, 9289, 9908, 10528],
        11: [2529, 3793, 5057, 6322, 7586, 8851, 9483, 10115, 10747],
        12: [2580, 3870, 5161, 6451, 7741, 9031, 9676, 10321, 10966],
        13: [2632, 3948, 5264, 6580, 7896, 9212, 9870, 10528, 11186],
        14: [2684, 4025, 5367, 6709, 8051, 9392, 10063, 10734, 11405],
        15: [2735, 4103, 5470, 6838, 8205, 9573, 10257, 10941, 11624],
    },
}


class _Scale:
    """A scale whose amount is the index of the range the income falls in."""

    thresholds = [-np.inf] + SHARES
    amounts = list(range(len(SHARES) + 1))


@pytest.mark.parametrize("month", sorted(TWC_UPPER_LIMITS))
def test_range_limits_match_twc_tables(month):
    table = TWC_UPPER_LIMITS[month]
    sizes = np.array(sorted(table))
    monthly_smi = (
        smi(sizes, np.array(["TX"] * len(sizes)), month, system.parameters) / 12
    )
    limits = np.array([table[size] for size in sizes], dtype=float)
    for i in range(len(SHARES)):
        at_limit = board_scale_amount(_Scale, limits[:, i], monthly_smi)
        above_limit = board_scale_amount(_Scale, limits[:, i] + 1, monthly_smi)
        assert (at_limit == i).all(), (month, SHARES[i], sizes[at_limit != i])
        assert (above_limit == i + 1).all(), (
            month,
            SHARES[i],
            sizes[above_limit != i + 1],
        )


def _board_scales():
    for board in TXCCSWorkforceBoardRegion:
        folder = BOARD / board.name.lower()
        if not folder.exists():
            continue
        for name in ("first_child", "additional_child"):
            yield pytest.param(folder / f"{name}.yaml", id=f"{folder.name}-{name}")


@pytest.mark.parametrize("path", list(_board_scales()))
def test_board_scales_rise_with_income(path):
    brackets = yaml.safe_load(path.read_text())["brackets"]
    dates = set().union(*(bracket["threshold"] for bracket in brackets))
    for date in sorted(dates):
        thresholds = [bracket["threshold"][date] for bracket in brackets]
        amounts = [bracket["amount"][date] for bracket in brackets]
        assert thresholds == sorted(thresholds), (date, thresholds)
        assert len(set(thresholds)) == len(thresholds), (date, thresholds)
        assert amounts == sorted(amounts), (date, amounts)


def test_every_applying_board_has_a_scale():
    applies = yaml.safe_load((BOARD / "applies.yaml").read_text())
    assert set(applies) - {"description", "metadata"} == {
        board.name for board in TXCCSWorkforceBoardRegion
    }
    for board in TXCCSWorkforceBoardRegion:
        start_dates = [
            date for date, value in applies[board.name].items() if value is True
        ]
        folder = BOARD / board.name.lower()
        if not start_dates:
            assert not folder.exists(), board.name
            continue
        for name in ("first_child", "additional_child"):
            brackets = yaml.safe_load((folder / f"{name}.yaml").read_text())["brackets"]
            for date in start_dates:
                assert all(date in bracket["amount"] for bracket in brackets), (
                    board.name,
                    name,
                    date,
                )
