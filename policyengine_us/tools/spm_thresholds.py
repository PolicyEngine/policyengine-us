from __future__ import annotations

from functools import lru_cache

import numpy as np

PUBLISHED_SPM_REFERENCE_THRESHOLDS = {
    2015: {
        "renter": 25_155.0,
        "owner_with_mortgage": 24_859.0,
        "owner_without_mortgage": 20_639.0,
    },
    2016: {
        "renter": 25_558.0,
        "owner_with_mortgage": 25_248.0,
        "owner_without_mortgage": 20_943.0,
    },
    2017: {
        "renter": 26_213.0,
        "owner_with_mortgage": 25_897.0,
        "owner_without_mortgage": 21_527.0,
    },
    2018: {
        "renter": 26_905.0,
        "owner_with_mortgage": 26_565.0,
        "owner_without_mortgage": 22_095.0,
    },
    2019: {
        "renter": 27_515.0,
        "owner_with_mortgage": 27_172.0,
        "owner_without_mortgage": 22_600.0,
    },
    2020: {
        "renter": 28_881.0,
        "owner_with_mortgage": 28_533.0,
        "owner_without_mortgage": 23_948.0,
    },
    2021: {
        "renter": 31_453.0,
        "owner_with_mortgage": 31_089.0,
        "owner_without_mortgage": 26_022.0,
    },
    2022: {
        "renter": 33_402.0,
        "owner_with_mortgage": 32_949.0,
        "owner_without_mortgage": 27_679.0,
    },
    2023: {
        "renter": 36_606.0,
        "owner_with_mortgage": 36_192.0,
        "owner_without_mortgage": 30_347.0,
    },
    2024: {
        "renter": 39_430.0,
        "owner_with_mortgage": 39_068.0,
        "owner_without_mortgage": 32_586.0,
    },
}

LATEST_PUBLISHED_SPM_THRESHOLD_YEAR = max(PUBLISHED_SPM_REFERENCE_THRESHOLDS)
REFERENCE_RAW_SCALE = 3**0.7


@lru_cache(maxsize=1)
def _get_cpi_u_parameter():
    from policyengine_us import CountryTaxBenefitSystem

    system = CountryTaxBenefitSystem()
    return system.parameters.gov.bls.cpi.cpi_u


def spm_equivalence_scale(num_adults, num_children):
    adults, children = np.broadcast_arrays(
        np.asarray(num_adults, dtype=float),
        np.asarray(num_children, dtype=float),
    )

    raw = np.zeros_like(adults, dtype=float)
    has_people = (adults + children) > 0
    with_children = has_people & (children > 0)

    single_adult_with_children = with_children & (adults <= 1)
    raw[single_adult_with_children] = (
        1.0
        + 0.8
        + 0.5 * np.maximum(children[single_adult_with_children] - 1, 0)
    ) ** 0.7

    multi_adult_with_children = with_children & ~single_adult_with_children
    raw[multi_adult_with_children] = (
        adults[multi_adult_with_children]
        + 0.5 * children[multi_adult_with_children]
    ) ** 0.7

    no_children = has_people & ~with_children
    one_adult = no_children & (adults <= 1)
    two_adults = no_children & (adults == 2)
    larger_adult_units = no_children & (adults > 2)

    raw[one_adult] = 1.0
    raw[two_adults] = 1.41
    raw[larger_adult_units] = adults[larger_adult_units] ** 0.7

    return raw / REFERENCE_RAW_SCALE


def get_spm_reference_thresholds(year: int, cpi_u_parameter=None) -> dict[str, float]:
    if year in PUBLISHED_SPM_REFERENCE_THRESHOLDS:
        return PUBLISHED_SPM_REFERENCE_THRESHOLDS[year].copy()

    if year < min(PUBLISHED_SPM_REFERENCE_THRESHOLDS):
        raise ValueError(
            f"No published SPM reference thresholds for {year}. "
            f"Earliest available year is {min(PUBLISHED_SPM_REFERENCE_THRESHOLDS)}."
        )

    cpi_u_parameter = cpi_u_parameter or _get_cpi_u_parameter()
    factor = float(
        cpi_u_parameter(f"{year}-02-01")
        / cpi_u_parameter(f"{LATEST_PUBLISHED_SPM_THRESHOLD_YEAR}-02-01")
    )
    latest_thresholds = PUBLISHED_SPM_REFERENCE_THRESHOLDS[
        LATEST_PUBLISHED_SPM_THRESHOLD_YEAR
    ]
    return {
        tenure: value * factor
        for tenure, value in latest_thresholds.items()
    }
