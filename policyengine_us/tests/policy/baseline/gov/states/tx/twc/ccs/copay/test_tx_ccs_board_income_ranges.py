"""Board parent share of cost scales meet TWC's income ranges and stay ordered.

Before TX3C, Texas Workforce Boards set parent share of cost amounts for the
SMI or FPG income ranges TWC published each Board Contract Year (WD 24-23
Attachment 2 for BCY 2024; the BCY 2025 ranges WD 20-24 sent for October 1 to
December 8, 2024). tx_ccs_board_copay rebuilds each SMI range limit from the
SMI in force that month. The first check runs board_scale_amount over every
SMI cell of both tables, family sizes 2 to 15, on each side of each limit, so
a change to the SMI parameter, the size factor or the rounding that moves any
limit by a dollar fails here. TWC's FPG limits follow no single rounding rule,
so the model reads them from fpg_income_limits.yaml; the FPG checks hold each
of those limits to the poverty guidelines and to TWC's 85% SMI limit, and run
the lookup over every cell. The other checks read the Board parameter files:
every Board scale must rise with income, every reduction must stay between 0
and 1, every Board that applies its own scale must have one, no Board's scale
may apply before BCY 2024, and every FPG threshold must name one of TWC's FPG
ranges. Property tests state what
board_scale_amount does for any chart, income and SMI: it returns one of the
chart's amounts, each limit separates its two ranges, the amount never falls
as income rises, and it never rises as SMI rises.
"""

from pathlib import Path
from types import SimpleNamespace

from hypothesis import given
from hypothesis import strategies as st
import numpy as np
import pytest
import yaml

from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.states.tx.twc.ccs.copay.tx_ccs_board_copay import (
    board_scale_amount,
    fpg_range_limit,
    smi_range_limit,
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
        limit = smi_range_limit(monthly_smi)
        at_limit = board_scale_amount(_Scale, limits[:, i], limit)
        above_limit = board_scale_amount(_Scale, limits[:, i] + 1, limit)
        assert (at_limit == i).all(), (month, SHARES[i], sizes[at_limit != i])
        assert (above_limit == i + 1).all(), (
            month,
            SHARES[i],
            sizes[above_limit != i + 1],
        )


# A chart: rising SMI shares above a first range that starts at $0, and rising
# amounts, one per range.
_charts = st.integers(min_value=1, max_value=9).flatmap(
    lambda ranges: st.builds(
        lambda shares, amounts: SimpleNamespace(
            thresholds=[-np.inf] + sorted(shares),
            amounts=sorted(amounts),
        ),
        st.lists(
            st.integers(min_value=1, max_value=100).map(lambda pct: pct / 100),
            min_size=ranges,
            max_size=ranges,
            unique=True,
        ),
        st.lists(
            st.integers(min_value=0, max_value=1_000),
            min_size=ranges + 1,
            max_size=ranges + 1,
        ),
    )
)
_incomes = st.floats(min_value=0, max_value=50_000, allow_nan=False)
_monthly_smis = st.floats(min_value=500, max_value=30_000, allow_nan=False)


def _amount(chart, income, monthly_smi):
    limit = smi_range_limit(np.array([monthly_smi]))
    return board_scale_amount(chart, np.array([income]), limit)[0]


@given(_charts, _incomes, _monthly_smis)
def test_amount_comes_from_the_chart(chart, income, monthly_smi):
    assert _amount(chart, income, monthly_smi) in chart.amounts


@given(_charts, _incomes, _incomes, _monthly_smis)
def test_amount_never_falls_as_income_rises(chart, income_a, income_b, monthly_smi):
    low, high = sorted([income_a, income_b])
    assert _amount(chart, low, monthly_smi) <= _amount(chart, high, monthly_smi)


@given(_charts, _incomes, _monthly_smis, _monthly_smis)
def test_amount_never_rises_as_smi_rises(chart, income, smi_a, smi_b):
    low, high = sorted([smi_a, smi_b])
    assert _amount(chart, income, high) <= _amount(chart, income, low)


@given(_charts, _monthly_smis, st.data())
def test_each_limit_separates_its_two_ranges(chart, monthly_smi, data):
    # Limits round to whole dollars, so a family at one limit can also sit at
    # the next share's limit; these hold either way.
    i = data.draw(st.integers(min_value=1, max_value=len(chart.amounts) - 1))
    limit = np.floor(monthly_smi * chart.thresholds[i] + 0.5)
    assert _amount(chart, limit, monthly_smi) <= chart.amounts[i - 1]
    assert _amount(chart, limit + 1, monthly_smi) >= chart.amounts[i]


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


@pytest.mark.parametrize("name", ["texas_rising_star", "part_time"])
def test_reductions_stay_between_zero_and_one(name):
    reduction = yaml.safe_load((BOARD / f"reduction/{name}.yaml").read_text())
    for board in TXCCSWorkforceBoardRegion:
        assert all(0 <= value <= 1 for value in reduction[board.name].values()), (
            name,
            board.name,
        )


def test_every_applying_board_has_a_scale():
    applies = system.parameters.gov.states.tx.twc.ccs.copay.board.applies
    assert set(applies.children) == {board.name for board in TXCCSWorkforceBoardRegion}
    for board in TXCCSWorkforceBoardRegion:
        values = applies.children[board.name].values_list
        # The model copies each parameter's earliest value back to 2015, so a
        # Board whose switch started true would apply its scale from 2015.
        assert not values[-1].value, board.name
        start_dates = [value.instant_str for value in values if value.value]
        folder = BOARD / board.name.lower()
        if not start_dates:
            assert not folder.exists(), board.name
            continue
        for name in ("first_child", "additional_child"):
            brackets = yaml.safe_load((folder / f"{name}.yaml").read_text())["brackets"]
            for date in start_dates:
                assert all(
                    date in map(str, bracket["amount"]) for bracket in brackets
                ), (board.name, name, date)


@pytest.mark.parametrize("instant", ["2015-01-01", "2023-09-30"])
def test_no_board_scale_applies_before_bcy_2024(instant):
    applies = system.parameters(instant).gov.states.tx.twc.ccs.copay.board.applies
    assert not any(applies[board.name] for board in TXCCSWorkforceBoardRegion)


FPG_PERCENTS = [50, 75, 100, 125, 150, 175, 185, 200]
FPG_TABLE_STARTS = ["2023-10-01", "2024-10-01"]


def _fpg_table(instant):
    return system.parameters(
        instant
    ).gov.states.tx.twc.ccs.copay.board.fpg_income_limits


def _twc_annual_guideline(instant, size):
    fpg = system.parameters(instant).gov.hhs.fpg
    first = fpg.first_person.CONTIGUOUS_US
    additional = fpg.additional_person.CONTIGUOUS_US
    if instant == "2024-10-01" and size > 8:
        # Intended exception: TWC's October 2024 table follows HHS's 2024
        # guidelines through family size 8, then adds Hawaii's amount for
        # each additional person ($6,190) instead of the contiguous states'
        # ($5,380). Boards assessed families against the printed table, so
        # the model keeps it.
        return first + 7 * additional + fpg.additional_person.HI * (size - 8)
    return first + additional * (size - 1)


@pytest.mark.parametrize("instant", FPG_TABLE_STARTS)
def test_fpg_limits_follow_the_poverty_guidelines(instant):
    # Each printed limit lies within a dollar of its share of the annual
    # guideline over 12 months. TWC prints * instead of any limit that would
    # pass 85% of SMI, the eligibility limit, and the model reads those as
    # never exceeded.
    table = _fpg_table(instant)
    for size in range(2, 16):
        annual = _twc_annual_guideline(instant, size)
        monthly_smi = smi(
            np.array([size]), np.array(["TX"]), instant, system.parameters
        )
        eligibility_limit = np.floor(0.85 * monthly_smi[0] / 12 + 0.5)
        for percent in FPG_PERCENTS:
            limit = table[str(size)][str(percent)]
            exact = percent / 100 * annual / 12
            if np.floor(exact + 0.5) > eligibility_limit:
                assert limit == np.inf, (instant, size, percent, limit)
            else:
                assert abs(limit - exact) < 1, (instant, size, percent, limit, exact)


class _FPGScale:
    """A scale whose amount is the index of the FPG range the income falls in."""

    thresholds = [-np.inf] + [percent / 100 for percent in FPG_PERCENTS]
    amounts = list(range(len(FPG_PERCENTS) + 1))


@pytest.mark.parametrize("instant", FPG_TABLE_STARTS)
def test_fpg_range_lookup_matches_the_table(instant):
    table = _fpg_table(instant)
    # TWC prints sizes 2 to 15. Sizes 1, 16 and 17 check that the formula
    # reads the nearest printed size, which is the model's choice, not TWC's.
    sizes = np.arange(1, 18)
    capped = np.clip(sizes, 2, 15)
    limit = fpg_range_limit(table[capped], capped)
    limits = np.array(
        [
            [table[str(size)][str(percent)] for percent in FPG_PERCENTS]
            for size in capped
        ]
    )
    for i in range(len(FPG_PERCENTS)):
        printed = np.isfinite(limits[:, i])
        income = np.where(printed, limits[:, i], 0)
        at_limit = board_scale_amount(_FPGScale, income, limit)
        above_limit = board_scale_amount(_FPGScale, income + 1, limit)
        assert (at_limit[printed] == i).all(), (instant, i, sizes[printed])
        assert (above_limit[printed] == i + 1).all(), (instant, i, sizes[printed])
    # Above the last printed limit, a family stays in the range that runs to
    # 85% of SMI.
    highest = board_scale_amount(_FPGScale, np.full(len(sizes), 1e9), limit)
    assert (highest == np.isfinite(limits).sum(axis=1)).all(), (instant, highest)


def test_fpg_board_thresholds_name_twc_ranges():
    flags = yaml.safe_load((BOARD / "uses_fpg_ranges.yaml").read_text())
    for board in TXCCSWorkforceBoardRegion:
        dates = [date for date, value in flags[board.name].items() if value is True]
        if not dates:
            continue
        for name in ("first_child", "additional_child"):
            brackets = yaml.safe_load(
                (BOARD / board.name.lower() / f"{name}.yaml").read_text()
            )["brackets"]
            for date in dates:
                for bracket in brackets:
                    threshold = bracket["threshold"][date]
                    if threshold == -np.inf:
                        continue
                    assert round(threshold * 100) in FPG_PERCENTS, (
                        board.name,
                        name,
                        date,
                        threshold,
                    )


def test_formula_reads_fpg_ranges_for_a_board_that_uses_them():
    # Greater Dallas's chart tests check two FPG limits. This moves Panhandle's
    # November 2024 scale onto TWC's FPG ranges and checks a family of one
    # adult and two children on each side of each printed limit.
    board = "gov.states.tx.twc.ccs.copay.board"
    when = "2024-10-01.2024-12-31"
    changes = {f"{board}.uses_fpg_ranges.PANHANDLE": {when: True}}
    for name in ("first_child", "additional_child"):
        for i, percent in enumerate(FPG_PERCENTS, start=1):
            changes[f"{board}.panhandle.{name}[{i}].threshold"] = {when: percent / 100}
    limits = [_fpg_table("2024-10-01")["3"][str(percent)] for percent in FPG_PERCENTS]
    incomes = [income for limit in limits for income in (limit, limit + 1)]
    people, spm_units, households = {}, {}, {}
    for n, income in enumerate(incomes):
        members = [f"adult_{n}", f"child_{n}_1", f"child_{n}_2"]
        people[members[0]] = {
            "age": {"2024": 30},
            "weekly_hours_worked_before_lsr": {"2024": 40},
            "employment_income": {"2024": income * 12},
        }
        for child, age in zip(members[1:], (3, 5)):
            people[child] = {
                "age": {"2024": age},
                "is_citizen_or_legal_immigrant": {"2024": True},
            }
        spm_units[f"spm_unit_{n}"] = {
            "members": members,
            "spm_unit_size": {"2024": 3},
        }
        households[f"household_{n}"] = {
            "members": members,
            "state_code": {"2024": "TX"},
            "tx_ccs_workforce_board_region": {"2024": "PANHANDLE"},
        }
    simulation = Simulation(
        situation={"people": people, "spm_units": spm_units, "households": households},
        reform=Reform.from_dict(changes, country_id="us"),
    )
    scales = simulation.tax_benefit_system.parameters(
        "2024-11-01"
    ).gov.states.tx.twc.ccs.copay.board.panhandle
    amounts = np.add(scales.first_child.amounts, scales.additional_child.amounts)
    expected = [amounts[i + side] for i in range(len(limits)) for side in (0, 1)]
    copay = simulation.calculate("tx_ccs_board_copay", "2024-11")
    assert list(copay) == expected, list(zip(incomes, copay, expected))
