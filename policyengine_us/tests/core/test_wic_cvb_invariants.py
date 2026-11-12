"""Check WIC CVB history across every package and drawn package vectors.

YAML examples check household amounts. These checks cover every public
package key in January 2018-September 2021 and October 2023-September 2026,
including legacy aliases that the food-package enum no longer assigns.
Hypothesis checks replacement arithmetic and vector isolation at fixed prices
across combinations of packages and fiscal years.

The table checks load only WIC's parameter subtree. Formula properties import
the package once and construct no additional tax-benefit systems or simulations.
"""

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from policyengine_core.parameters import ParameterNode

CHILD_KEYS = (
    "CHILD",
    "CHILD_12_23_MONTHS",
    "CHILD_24_59_MONTHS",
    "IV-A",
    "IV-B",
)
PREGNANT_POSTPARTUM_KEYS = (
    "PREGNANT",
    "PREGNANT_SINGLETON",
    "POSTPARTUM",
    "POSTPARTUM_NON_BREASTFEEDING",
    "V",
    "VI",
)
BREASTFEEDING_KEYS = (
    "PREGNANT_MULTIPLE_FETUSES",
    "BREASTFEEDING",
    "PARTIALLY_BREASTFEEDING",
    "FULLY_BREASTFEEDING",
    "VII",
)
MULTIPLES_KEY = "FULLY_BREASTFEEDING_MULTIPLES"
ZERO_CVB_KEYS = (
    "INFANT",
    "INFANT_AVERAGE",
    "INFANT_0_3_FULLY_FORMULA_FED",
    "INFANT_4_5_FULLY_FORMULA_FED",
    "INFANT_0_3_PARTIALLY_BREASTFED",
    "INFANT_4_5_PARTIALLY_BREASTFED",
    "INFANT_6_11_PARTIALLY_BREASTFED",
    "INFANT_0_5_FULLY_BREASTFED",
    "INFANT_6_11_FULLY_FORMULA_FED",
    "INFANT_6_11_FULLY_BREASTFED",
    "I-FF-A",
    "I-FF-B",
    "I-BF/FF-A",
    "I-BF/FF-B",
    "I-BF/FF-C",
    "I-BF-A",
    "I-BF-B",
    "II-FF",
    "II-BF/FF",
    "II-BF",
    "NONE",
)
ALL_KEYS = (
    *CHILD_KEYS,
    *PREGNANT_POSTPARTUM_KEYS,
    *BREASTFEEDING_KEYS,
    MULTIPLES_KEY,
    *ZERO_CVB_KEYS,
)
PROPERTY_SETTINGS = settings(max_examples=30, deadline=None, derandomize=True)
PACKAGE_VECTORS = st.lists(st.sampled_from(ALL_KEYS), min_size=1, max_size=40)


def _months(first_year, first_month, last_year, last_month):
    first = first_year * 12 + first_month - 1
    last = last_year * 12 + last_month - 1
    return tuple(
        f"{month // 12}-{month % 12 + 1:02d}" for month in range(first, last + 1)
    )


AMENDED_MONTHS = (
    *_months(2021, 10, 2023, 9),
    *_months(2026, 10, 2027, 9),
)


@pytest.fixture(scope="module")
def wic_parameters():
    path = Path(__file__).resolve().parents[2] / "parameters/gov/usda/wic"
    return ParameterNode("wic", directory_path=str(path))


def _expected_cvb(child, pregnant_postpartum, breastfeeding):
    return {
        **dict.fromkeys(CHILD_KEYS, child),
        **dict.fromkeys(PREGNANT_POSTPARTUM_KEYS, pregnant_postpartum),
        **dict.fromkeys(BREASTFEEDING_KEYS, breastfeeding),
        MULTIPLES_KEY: breastfeeding * 1.5,
        **dict.fromkeys(ZERO_CVB_KEYS, 0),
    }


def _calculate(wic_parameters, month, packages, replaces=None):
    # Keep the raw 2018 package prices fixed to isolate the CVB change.
    from policyengine_us.variables.gov.usda.wic.wic_if_takes_up import (
        wic_if_takes_up,
    )

    snapshot = wic_parameters(f"{month}-01")
    cvb = SimpleNamespace(
        current=snapshot.cvb.current,
        included_in_value=snapshot.cvb.included_in_value,
        replaces_included_value=(
            snapshot.cvb.replaces_included_value if replaces is None else replaces
        ),
    )
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            usda=SimpleNamespace(
                wic=SimpleNamespace(
                    value=snapshot.value,
                    cvb=cvb,
                    abolish_wic=snapshot.abolish_wic,
                )
            )
        )
    )

    def person(name, period):
        assert name == "wic_food_package_str"
        assert period == month
        return np.asarray(packages)

    return wic_if_takes_up.formula(person, month, lambda period: parameters)


def test_cvb_tables_cover_every_package_key(wic_parameters):
    expected_keys = set(ALL_KEYS)
    assert len(expected_keys) == len(ALL_KEYS)
    assert set(wic_parameters.value.children) == expected_keys
    assert set(wic_parameters.cvb.current.children) == expected_keys
    assert set(wic_parameters.cvb.included_in_value.children) == expected_keys


def test_unchanged_months_retain_main_cvb_values(wic_parameters):
    # Main disables CVB replacement through September 2021.
    for month in _months(2018, 1, 2021, 9):
        cvb = wic_parameters(f"{month}-01").cvb
        assert not cvb.replaces_included_value, month
        for key in ALL_KEYS:
            assert cvb.current[key] == 0, (month, key)

    # Main retains its FY2024 table through FY2026, apart from the
    # pregnant/postpartum increase in October 2025.
    for month in _months(2023, 10, 2026, 9):
        cvb = wic_parameters(f"{month}-01").cvb
        pregnant_postpartum = 47 if month < "2025-10" else 48
        expected = _expected_cvb(26, pregnant_postpartum, 52)
        assert cvb.replaces_included_value, month
        for key, value in expected.items():
            assert cvb.current[key] == value, (month, key)


@pytest.mark.parametrize(
    "first_month,last_month,amounts",
    [
        ("2021-10", "2022-09", (24, 43, 47)),
        ("2022-10", "2023-09", (25, 44, 49)),
        ("2026-10", "2027-09", (27, 48, 53)),
    ],
)
def test_fiscal_year_tables_cover_all_aliases(
    wic_parameters, first_month, last_month, amounts
):
    for month in (first_month, last_month):
        cvb = wic_parameters(f"{month}-01").cvb
        assert cvb.replaces_included_value, month
        for key, value in _expected_cvb(*amounts).items():
            assert cvb.current[key] == value, (month, key)


@PROPERTY_SETTINGS
@given(month=st.sampled_from(AMENDED_MONTHS), packages=PACKAGE_VECTORS)
def test_cvb_replacement_counts_current_benefit_once(wic_parameters, month, packages):
    cvb = wic_parameters(f"{month}-01").cvb
    result = _calculate(wic_parameters, month, packages)
    without_replacement = _calculate(wic_parameters, month, packages, replaces=False)
    included = np.array([cvb.included_in_value[key] for key in packages])
    current = np.array([cvb.current[key] for key in packages])

    assert np.all(result >= 0)
    assert np.all(result >= without_replacement)
    np.testing.assert_allclose(
        result - without_replacement + included, current, atol=1e-10
    )
    zero_cvb = np.isin(packages, ZERO_CVB_KEYS)
    np.testing.assert_array_equal(current[zero_cvb], 0)
    np.testing.assert_array_equal(result[zero_cvb], without_replacement[zero_cvb])

    reversed_result = _calculate(wic_parameters, month, list(reversed(packages)))
    np.testing.assert_array_equal(reversed_result, result[::-1])


@PROPERTY_SETTINGS
@given(
    boundary=st.sampled_from(
        [
            ("2021-09", "2021-10"),
            ("2022-09", "2022-10"),
            ("2026-09", "2026-10"),
        ]
    ),
    packages=PACKAGE_VECTORS,
)
def test_new_cvb_dates_never_reduce_package_value(wic_parameters, boundary, packages):
    previous = _calculate(wic_parameters, boundary[0], packages)
    current = _calculate(wic_parameters, boundary[1], packages)
    assert np.all(current >= previous)
    zero_cvb = np.isin(packages, ZERO_CVB_KEYS)
    np.testing.assert_array_equal(current[zero_cvb], previous[zero_cvb])
