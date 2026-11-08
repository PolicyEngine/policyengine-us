"""Invariants for the 2018-2026 histories of state employer unemployment taxes.

The tables below copy the new-employer rates and taxable wage bases that state
agencies published, from the sources cited in each parameter file, so these
tests compare the model with those publications and not with its own
parameters. Where new employers take their industry's rate, the tables hold the
state's new-employer rule applied to the statewide averages that its agencies
or the U.S. Department of Labor published.

Three tests run without a simulation:

1. Schedule: in every month from 2015 through 2026, every jurisdiction's
   default rate and taxable wage base equal the published value for that
   month, and so do New Jersey's employer TDI and workforce fund rates, Rhode
   Island's Job Development Fund rate and 2019 adjustment, and Alaska's
   employee contribution rate. Apart from Minnesota's wage base, which keeps
   DEED's 2014-2017 values, the parameters start in 2018, so 2015-2017 read
   the value in force on January 1, 2018, an intended approximation that this
   test pins.
2. Dates: every stored value of a parameter that an annual rate averages
   begins a calendar quarter. The annual rates read only the four quarter
   starts, so this keeps them equal to the average of all twelve months.
3. New-employer rules: where new employers take their industry's rate, the
   published default equals the state's rule rebuilt from its published
   inputs, and no published default falls below the statutory minimum.

Hypothesis draws batches of workers, each with wages, a raise and a state; a
seeded population puts two workers in every jurisdiction. Each batch runs as
one vectorized simulation covering SIMULATED_YEARS, which include the July-June
rate changes. For every worker and year:

4. Differential: each employer unemployment tax equals the published rate,
   averaged over the four quarter starts, times wages up to the published wage
   base; so do New Jersey's employer TDI and workforce fund contributions,
   Rhode Island's Job Development Fund tax and Alaska's employee contribution.
5. Bounds: each tax lies between zero and its highest quarterly rate times
   positive wages, and wages at or below zero owe nothing.
6. Monotonicity: no tax falls when wages rise.
7. Agreement: the employer-total paths equal the worker paths when the
   employer-total taxable wages equal the worker's.
8. Geography: outside its jurisdiction, each jurisdiction's tax is zero.
"""

from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.variables.gov.states.tax.payroll.unemployment._jurisdictions import (
    STATE_UNEMPLOYMENT_TAX_JURISDICTIONS,
)

TOLERANCE = 0.01  # dollars
FIRST_YEAR = 2015  # policyengine_us.tools.parameters.FIRST_MODELED_YEAR
FIRST_PUBLISHED_YEAR = 2018
LAST_YEAR = 2026
MONTHS = range(1, 13)
QUARTER_START_MONTHS = (1, 4, 7, 10)

# Published new-employer rate and taxable wage base for each jurisdiction and
# year. A rate is one number, or four numbers when the rate changes inside the
# calendar year: the rates in force at the starts of the four quarters.
# BEGIN PUBLISHED_SUTA (generated from the curated source table)
PUBLISHED_SUTA = {
    "AK": {
        2018: (0.01, 39_500),
        2019: (0.01, 39_900),
        2020: (0.01, 41_500),
        2021: (0.0141, 43_600),
        2022: (0.0153, 45_200),
        2023: (0.0104, 47_100),
        2024: (0.01, 49_700),
        2025: (0.01, 51_700),
        2026: (0.01, 54_200),
    },
    "AL": {
        2018: (0.027, 8_000),
        2019: (0.027, 8_000),
        2020: (0.027, 8_000),
        2021: (0.027, 8_000),
        2022: (0.027, 8_000),
        2023: (0.027, 8_000),
        2024: (0.027, 8_000),
        2025: (0.027, 8_000),
        2026: (0.027, 8_000),
    },
    "AR": {
        2018: (0.032, 10_000),
        2019: (0.032, 10_000),
        2020: (0.031, 7_000),
        2021: (0.031, 10_000),
        2022: (0.031, 10_000),
        2023: ((0.031, 0.031, 0.03025, 0.03025), 7_000),
        2024: ((0.02025, 0.02025, 0.02, 0.02), 7_000),
        2025: (0.02, 7_000),
        2026: (0.02, 7_000),
    },
    "AZ": {
        2018: (0.02, 7_000),
        2019: (0.02, 7_000),
        2020: (0.02, 7_000),
        2021: (0.02, 7_000),
        2022: (0.02, 7_000),
        2023: (0.02, 8_000),
        2024: (0.02, 8_000),
        2025: (0.02, 8_000),
        2026: (0.02, 8_000),
    },
    "CA": {
        2018: (0.034, 7_000),
        2019: (0.034, 7_000),
        2020: (0.034, 7_000),
        2021: (0.034, 7_000),
        2022: (0.034, 7_000),
        2023: (0.034, 7_000),
        2024: (0.034, 7_000),
        2025: (0.034, 7_000),
        2026: (0.034, 7_000),
    },
    "CO": {
        2018: (0.017, 12_600),
        2019: (0.017, 13_100),
        2020: (0.017, 13_600),
        2021: (0.017, 13_600),
        2022: (0.017, 17_000),
        2023: (0.017, 20_400),
        2024: (0.0305, 23_800),
        2025: (0.0305, 27_200),
        2026: (0.0305, 30_600),
    },
    "CT": {
        2018: (0.036, 15_000),
        2019: (0.034, 15_000),
        2020: (0.032, 15_000),
        2021: (0.03, 15_000),
        2022: (0.03, 15_000),
        2023: (0.028, 15_000),
        2024: (0.025, 25_000),
        2025: (0.022, 26_100),
        2026: (0.019, 27_000),
    },
    "DC": {
        2018: (0.027, 9_000),
        2019: (0.027, 9_000),
        2020: (0.027, 9_000),
        2021: (0.027, 9_000),
        2022: (0.027, 9_000),
        2023: (0.027, 9_000),
        2024: (0.027, 9_000),
        2025: (0.027, 9_000),
        2026: (0.027, 9_000),
    },
    "DE": {
        2018: (0.016, 16_500),
        2019: (0.015, 16_500),
        2020: (0.018, 16_500),
        2021: (0.018, 16_500),
        2022: (0.018, 14_500),
        2023: (0.012, 10_500),
        2024: (0.012, 10_500),
        2025: (0.012, 12_500),
        2026: (0.01, 14_500),
    },
    "FL": {
        2018: (0.027, 7_000),
        2019: (0.027, 7_000),
        2020: (0.027, 7_000),
        2021: (0.027, 7_000),
        2022: (0.027, 7_000),
        2023: (0.027, 7_000),
        2024: (0.027, 7_000),
        2025: (0.027, 7_000),
        2026: (0.027, 7_000),
    },
    "GA": {
        2018: (0.0264, 9_500),
        2019: (0.0264, 9_500),
        2020: (0.0264, 9_500),
        2021: (0.0264, 9_500),
        2022: (0.0264, 9_500),
        2023: (0.027, 9_500),
        2024: (0.0264, 9_500),
        2025: (0.0264, 9_500),
        2026: (0.0264, 9_500),
    },
    "HI": {
        2018: (0.024, 45_900),
        2019: (0.024, 46_800),
        2020: (0.024, 48_100),
        2021: (0.03, 47_400),
        2022: (0.03, 51_600),
        2023: (0.04, 56_700),
        2024: (0.03, 59_100),
        2025: (0.024, 62_000),
        2026: (0.024, 64_500),
    },
    "IA": {
        2018: (0.01, 29_900),
        2019: (0.01, 30_600),
        2020: (0.01, 31_600),
        2021: (0.01, 32_400),
        2022: (0.01, 34_800),
        2023: (0.01, 36_100),
        2024: (0.01, 38_200),
        2025: (0.01, 39_500),
        2026: (0.01, 20_400),
    },
    "ID": {
        2018: (0.01, 38_200),
        2019: (0.01, 40_000),
        2020: (0.01, 41_600),
        2021: (0.01, 43_000),
        2022: (0.01, 46_500),
        2023: (0.01, 49_900),
        2024: (0.01, 53_500),
        2025: (0.01, 55_300),
        2026: (0.01, 58_300),
    },
    "IL": {
        2018: (0.03225, 12_960),
        2019: (0.03175, 12_960),
        2020: (0.03125, 12_740),
        2021: (0.03175, 12_960),
        2022: (0.03525, 12_960),
        2023: (0.0395, 13_271),
        2024: (0.0395, 13_590),
        2025: (0.0365, 13_916),
        2026: (0.0335, 14_250),
    },
    "IN": {
        2018: (0.025, 9_500),
        2019: (0.025, 9_500),
        2020: (0.025, 9_500),
        2021: (0.025, 9_500),
        2022: (0.025, 9_500),
        2023: (0.025, 9_500),
        2024: (0.025, 9_500),
        2025: (0.025, 9_500),
        2026: (0.025, 9_500),
    },
    "KS": {
        2018: (0.027, 14_000),
        2019: (0.027, 14_000),
        2020: (0.027, 14_000),
        2021: (0.027, 14_000),
        2022: (0.027, 14_000),
        2023: (0.027, 14_000),
        2024: (0.027, 14_000),
        2025: (0.0175, 14_000),
        2026: (0.0175, 15_100),
    },
    "KY": {
        2018: (0.027, 10_200),
        2019: (0.027, 10_500),
        2020: (0.027, 10_800),
        2021: (0.027, 10_800),
        2022: (0.027, 10_800),
        2023: (0.027, 11_100),
        2024: (0.027, 11_400),
        2025: (0.027, 11_700),
        2026: (0.027, 12_000),
    },
    "LA": {
        2018: (0.0154, 7_700),
        2019: (0.0144, 7_700),
        2020: (0.0131, 7_700),
        2021: (0.0128, 7_700),
        2022: (0.0133, 7_700),
        2023: (0.0129, 7_700),
        2024: (0.013, 7_700),
        2025: (0.0123, 7_700),
        2026: (0.0125, 7_000),
    },
    "MA": {
        2018: (0.0213, 15_000),
        2019: (0.0242, 15_000),
        2020: (0.0242, 15_000),
        2021: (0.0242, 15_000),
        2022: (0.0242, 15_000),
        2023: (0.0145, 15_000),
        2024: (0.0187, 15_000),
        2025: (0.0213, 15_000),
        2026: (0.0242, 15_000),
    },
    "MD": {
        2018: (0.026, 8_500),
        2019: (0.026, 8_500),
        2020: (0.026, 8_500),
        2021: (0.023, 8_500),
        2022: (0.023, 8_500),
        2023: (0.023, 8_500),
        2024: (0.026, 8_500),
        2025: (0.026, 8_500),
        2026: (0.0245, 8_500),
    },
    "ME": {
        2018: (0.018, 12_000),
        2019: (0.0183, 12_000),
        2020: (0.0186, 12_000),
        2021: (0.0211, 12_000),
        2022: (0.0224, 12_000),
        2023: (0.0197, 12_000),
        2024: (0.0204, 12_000),
        2025: (0.0211, 12_000),
        2026: (0.0223, 12_000),
    },
    "MI": {
        2018: (0.0387, 9_000),
        2019: (0.0386, 9_000),
        2020: (0.027, 9_000),
        2021: (0.027, 9_500),
        2022: (0.027, 9_500),
        2023: (0.027, 9_500),
        2024: (0.027, 9_500),
        2025: (0.027, 9_000),
        2026: (0.027, 9_000),
    },
    "MN": {
        2018: (0.0116, 32_000),
        2019: (0.0111, 34_000),
        2020: (0.0107, 35_000),
        2021: (0.0109, 35_000),
        2022: (0.01, 38_000),
        2023: (0.01, 40_000),
        2024: (0.01, 42_000),
        2025: (0.01, 43_000),
        2026: (0.0153, 44_000),
    },
    "MO": {
        2018: (0.02511, 12_500),
        2019: (0.02376, 12_000),
        2020: (0.02376, 11_500),
        2021: (0.02376, 11_000),
        2022: (0.02376, 11_000),
        2023: (0.02511, 10_500),
        2024: (0.02376, 10_000),
        2025: (0.02376, 9_500),
        2026: (0.02376, 9_000),
    },
    "MS": {
        2018: (0.01, 14_000),
        2019: (0.01, 14_000),
        2020: (0.01, 14_000),
        2021: (0.01, 14_000),
        2022: (0.01, 14_000),
        2023: (0.01, 14_000),
        2024: (0.01, 14_000),
        2025: (0.01, 14_000),
        2026: (0.01, 14_000),
    },
    "MT": {
        2018: (0.0132, 32_000),
        2019: (0.0112, 33_000),
        2020: (0.0112, 34_100),
        2021: (0.0112, 35_300),
        2022: (0.0112, 38_100),
        2023: (0.0112, 40_500),
        2024: (0.0112, 43_000),
        2025: (0.0112, 45_100),
        2026: (0.01, 47_300),
    },
    "NC": {
        2018: (0.01, 23_500),
        2019: (0.01, 24_300),
        2020: (0.01, 25_200),
        2021: (0.01, 26_000),
        2022: (0.01, 28_000),
        2023: (0.01, 29_600),
        2024: (0.01, 31_400),
        2025: (0.01, 32_600),
        2026: (0.01, 34_200),
    },
    "NE": {
        2018: (0.0125, 9_000),
        2019: (0.0125, 9_000),
        2020: (0.0125, 9_000),
        2021: (0.0125, 9_000),
        2022: (0.0125, 9_000),
        2023: (0.0125, 9_000),
        2024: (0.0125, 9_000),
        2025: (0.0125, 9_000),
        2026: (0.0125, 9_000),
    },
    "NH": {
        2018: ((0.017, 0.017, 0.017, 0.012), 14_000),
        2019: (0.012, 14_000),
        2020: ((0.012, 0.017, 0.032, 0.032), 14_000),
        2021: (0.027, 14_000),
        2022: ((0.027, 0.027, 0.027, 0.022), 14_000),
        2023: ((0.022, 0.017, 0.017, 0.017), 14_000),
        2024: (0.017, 14_000),
        2025: (0.017, 14_000),
        2026: (0.017, 14_000),
    },
    "NJ": {
        2018: (0.026825, 33_700),
        2019: (0.026825, 34_400),
        2020: (0.026825, 35_300),
        2021: (0.026825, 36_200),
        2022: ((0.026825, 0.026825, 0.029825, 0.029825), 39_800),
        2023: ((0.029825, 0.029825, 0.032825, 0.032825), 41_100),
        2024: ((0.032825, 0.032825, 0.029825, 0.029825), 42_300),
        2025: ((0.029825, 0.029825, 0.026825, 0.026825), 43_300),
        2026: (0.026825, 44_800),
    },
    "NM": {
        2018: (0.01, 24_200),
        2019: (0.01, 24_800),
        2020: (0.01, 25_800),
        2021: (0.01, 27_000),
        2022: (0.01, 28_700),
        2023: (0.01, 30_100),
        2024: (0.01, 31_700),
        2025: (0.01, 33_200),
        2026: (0.01, 34_800),
    },
    "NV": {
        2018: (0.0295, 30_500),
        2019: (0.0295, 31_200),
        2020: (0.0295, 32_500),
        2021: (0.0295, 33_400),
        2022: (0.0295, 36_600),
        2023: (0.0295, 40_100),
        2024: (0.0295, 40_600),
        2025: (0.0295, 41_800),
        2026: (0.0295, 43_700),
    },
    "NY": {
        2018: (0.03525, 11_100),
        2019: (0.03125, 11_400),
        2020: (0.03125, 11_600),
        2021: (0.04025, 11_800),
        2022: (0.04025, 12_000),
        2023: (0.04025, 12_300),
        2024: (0.04025, 12_500),
        2025: (0.04025, 12_800),
        2026: (0.04025, 17_600),
    },
    "OH": {
        2018: (0.027, 9_500),
        2019: (0.027, 9_500),
        2020: (0.027, 9_000),
        2021: (0.027, 9_000),
        2022: (0.027, 9_000),
        2023: (0.027, 9_000),
        2024: (0.027, 9_000),
        2025: (0.027, 9_000),
        2026: (0.0285, 9_000),
    },
    "OK": {
        2018: (0.015, 17_600),
        2019: (0.015, 18_100),
        2020: (0.015, 18_700),
        2021: (0.015, 24_000),
        2022: (0.015, 24_800),
        2023: (0.015, 25_700),
        2024: (0.015, 27_000),
        2025: (0.015, 28_200),
        2026: (0.015, 25_000),
    },
    "OR": {
        2018: (0.024, 39_300),
        2019: (0.024, 40_600),
        2020: (0.021, 42_100),
        2021: (0.026, 43_800),
        2022: (0.024, 47_700),
        2023: (0.021, 50_900),
        2024: (0.024, 52_800),
        2025: (0.024, 54_300),
        2026: (0.024, 56_700),
    },
    "PA": {
        2018: (0.03689, 10_000),
        2019: (0.03689, 10_000),
        2020: (0.03689, 10_000),
        2021: (0.03689, 10_000),
        2022: (0.03689, 10_000),
        2023: (0.03822, 10_000),
        2024: (0.03822, 10_000),
        2025: (0.03822, 10_000),
        2026: (0.03822, 10_000),
    },
    "RI": {
        2018: (0.015, 23_000),
        2019: (0.0117, 23_600),
        2020: (0.0106, 24_000),
        2021: (0.0095, 24_600),
        2022: (0.0098, 24_600),
        2023: (0.0088, 28_200),
        2024: (0.0079, 29_200),
        2025: (0.01, 29_800),
        2026: (0.01, 30_800),
    },
    "SC": {
        2018: (0.0103, 14_000),
        2019: (0.0081, 14_000),
        2020: (0.0049, 14_000),
        2021: (0.0049, 14_000),
        2022: (0.0049, 14_000),
        2023: (0.0039, 14_000),
        2024: (0.0035, 14_000),
        2025: (0.01, 14_000),
        2026: (0.01, 14_000),
    },
    "SD": {
        2018: (0.012, 15_000),
        2019: (0.012, 15_000),
        2020: (0.012, 15_000),
        2021: (0.012, 15_000),
        2022: (0.012, 15_000),
        2023: (0.012, 15_000),
        2024: (0.012, 15_000),
        2025: (0.012, 15_000),
        2026: (0.012, 15_000),
    },
    "TN": {
        2018: (0.027, 7_000),
        2019: (0.027, 7_000),
        2020: (0.027, 7_000),
        2021: (0.027, 7_000),
        2022: (0.027, 7_000),
        2023: (0.027, 7_000),
        2024: (0.027, 7_000),
        2025: (0.027, 7_000),
        2026: (0.027, 7_000),
    },
    "TX": {
        2018: (0.027, 9_000),
        2019: (0.027, 9_000),
        2020: (0.027, 9_000),
        2021: (0.027, 9_000),
        2022: (0.027, 9_000),
        2023: (0.027, 9_000),
        2024: (0.027, 9_000),
        2025: (0.027, 9_000),
        2026: (0.027, 9_000),
    },
    "UT": {
        2018: (0.011, 34_300),
        2019: (0.011, 35_300),
        2020: (0.011, 36_600),
        2021: (0.012, 38_900),
        2022: (0.014, 41_600),
        2023: (0.014, 44_800),
        2024: (0.014, 47_000),
        2025: (0.013, 48_900),
        2026: (0.012, 50_700),
    },
    "VA": {
        2018: (0.0251, 8_000),
        2019: (0.0251, 8_000),
        2020: (0.025, 8_000),
        2021: (0.0273, 8_000),
        2022: (0.0273, 8_000),
        2023: (0.0253, 8_000),
        2024: (0.025, 8_000),
        2025: (0.0245, 8_000),
        2026: (0.0245, 8_000),
    },
    "VT": {
        2018: (0.01, 17_600),
        2019: (0.01, 15_600),
        2020: (0.01, 16_100),
        2021: (0.01, 14_100),
        2022: (0.01, 15_500),
        2023: (0.01, 13_500),
        2024: (0.01, 14_300),
        2025: (0.01, 14_800),
        2026: (0.01, 15_400),
    },
    "WA": {
        2018: (0.0115, 47_300),
        2019: (0.0115, 49_800),
        2020: (0.0114, 52_700),
        2021: (0.0135, 56_500),
        2022: (0.0154, 62_500),
        2023: (0.0136, 67_600),
        2024: (0.0141, 68_500),
        2025: (0.0137, 72_800),
        2026: (0.0149, 78_200),
    },
    "WI": {
        2018: (0.0305, 14_000),
        2019: (0.0305, 14_000),
        2020: (0.0305, 14_000),
        2021: (0.0305, 14_000),
        2022: (0.0305, 14_000),
        2023: (0.0305, 14_000),
        2024: (0.0305, 14_000),
        2025: (0.0305, 14_000),
        2026: (0.0305, 14_000),
    },
    "PR": {
        2018: (0.031, 7_000),
        2019: (0.029, 7_000),
        2020: (0.028, 7_000),
        2021: (0.028, 7_000),
        2022: (0.027, 7_000),
        2023: (0.033, 7_000),
        2024: (0.034, 7_000),
        2025: (0.031, 7_000),
        2026: (0.028, 7_000),
    },
    "VI": {
        2018: (0.02, 24_200),
        2019: (0.02, 26_500),
        2020: (0.02, 28_900),
        2021: (0.02, 32_500),
        2022: (0.02, 30_800),
        2023: (0.02, 30_200),
        2024: (0.02, 31_000),
        2025: (0.02, 31_100),
        2026: (0.02, 32_100),
    },
}
# END PUBLISHED_SUTA

# Minnesota's wage base keeps its 2015-2017 values (DEED, history of tax rate
# factors); every other parameter reads its 2018 value in those years.
PRE_2018_WAGE_BASE = {"MN": {2015: 30_000, 2016: 31_000, 2017: 32_000}}

# New Jersey Department of Labor and Workforce Development, rate information:
# new-employer TDI rate and workforce development and supplemental workforce
# fund rate, both on the UI taxable wage base.
NJ_EMPLOYER_TDI_RATE = 0.005
NJ_EMPLOYER_WORKFORCE_RATE = 0.001175

# Rhode Island Job Development Fund assessment of 0.21%, with the 0.08%
# adjustment that applied for 2019 only (R.I. Gen. Laws 28-43-8.5; DLT 2019
# rates; Division of Taxation ADV 2019-37).
RI_JDF_RATE = {2019: 0.0029}
RI_JDF_DEFAULT_RATE = 0.0021

# Alaska employee unemployment insurance contribution rate (AS 23.20.290(d);
# DOLWD actuarial report Table 1.3 and new-employer rate notices).
AK_EMPLOYEE_RATE = {2022: 0.0056, 2023: 0.0051}
AK_EMPLOYEE_DEFAULT_RATE = 0.005

SIMULATED_YEARS = (2018, 2022, 2026)

CODES = [code for _, code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS]
GROUP = {code: group for group, code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS}
SLUG = {code: slug for _, code, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS}
P = system.parameters.gov


def _unemployment(code):
    return getattr(getattr(P, GROUP[code]), SLUG[code]).tax.payroll.unemployment


def _published(code, year):
    return PUBLISHED_SUTA[code][max(year, FIRST_PUBLISHED_YEAR)]


def _quarterly_rates(code, year):
    rate, _ = _published(code, year)
    return rate if isinstance(rate, tuple) else (rate,) * 4


def _annual_rate(code, year):
    return float(np.mean(_quarterly_rates(code, year)))


def _rate_in_month(code, year, month):
    if year < FIRST_PUBLISHED_YEAR:
        # Backdating copies the first stored value to earlier years.
        return _quarterly_rates(code, FIRST_PUBLISHED_YEAR)[0]
    return _quarterly_rates(code, year)[(month - 1) // 3]


def _wage_base(code, year):
    return PRE_2018_WAGE_BASE.get(code, {}).get(year, _published(code, year)[1])


def _instants():
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        for month in MONTHS:
            yield year, month, f"{year}-{month:02d}-01"


def test_every_jurisdiction_has_a_published_history():
    assert sorted(PUBLISHED_SUTA) == sorted(CODES)
    for code, table in PUBLISHED_SUTA.items():
        assert sorted(table) == list(range(FIRST_PUBLISHED_YEAR, LAST_YEAR + 1)), code


def test_stored_histories_match_published_tables_in_every_month():
    nj = P.states.nj.tax.payroll
    ri = P.states.ri.tax.payroll.job_development_fund
    ak = P.states.ak.tax.payroll.unemployment
    for year, month, instant in _instants():
        for code in CODES:
            parameters = _unemployment(code)
            assert parameters.default_rate(instant) == _rate_in_month(
                code, year, month
            ), (code, instant)
            assert parameters.taxable_wage_base(instant) == _wage_base(code, year), (
                code,
                instant,
            )
        assert nj.temporary_disability_insurance.employer_rate(instant) == (
            NJ_EMPLOYER_TDI_RATE
        )
        assert nj.workforce_development.employer_rate(instant) == (
            NJ_EMPLOYER_WORKFORCE_RATE
        )
        assert ri.employer_rate(instant) + ri.adjustment_rate(instant) == (
            RI_JDF_RATE.get(year, RI_JDF_DEFAULT_RATE)
        ), instant
        assert ak.employee_rate(instant) == AK_EMPLOYEE_RATE.get(
            year, AK_EMPLOYEE_DEFAULT_RATE
        ), instant


def test_quarter_averaged_parameters_change_only_at_quarter_starts():
    # A value dated inside a quarter would need the annual rate to read more
    # than the four quarter starts.
    nj = P.states.nj.tax.payroll
    averaged = [_unemployment(code).default_rate for code in CODES] + [
        nj.temporary_disability_insurance.employer_rate,
        nj.workforce_development.employer_rate,
    ]
    for parameter in averaged:
        for entry in parameter.values_list:
            _, month, day = entry.instant_str.split("-")
            assert int(month) in QUARTER_START_MONTHS and day == "01", (
                parameter.name,
                entry.instant_str,
            )


# Minimum new-employer rates, in percent: AS 23.20.290(c); R.S. 23:1535(B);
# Minn. Stat. 268.051, subd. 5(a); MCA 39-51-1217(4); NMSA 51-1-11(G), which
# also caps the rate at 5.4%; Utah Code 35A-4-303(4)(b)(iii); and, for the
# experience part of Washington's rate, RCW 50.29.025(1)(d)(i) and WAC
# 192-320-025(4)(b).
MINIMUM_NEW_EMPLOYER_RATE = {
    "AK": Decimal("1"),
    "LA": Decimal("1"),
    "MN": Decimal("1"),
    "MT": Decimal("1"),
    "NM": Decimal("1"),
    "UT": Decimal("1.1"),
    "WA": Decimal("1"),
}
NM_MAXIMUM_NEW_EMPLOYER_RATE = Decimal("5.4")
# Statewide averages in percent, 2018 to 2026, as each parameter file cites
# them: the U.S. Department of Labor's average employer contribution rates on
# taxable wages for Louisiana, Minnesota and New Mexico (its estimates for
# 2026), and the Montana Department of Labor and Industry's average for the
# rate schedule in effect.
STATEWIDE_AVERAGE_RATE = {
    "LA": ("1.54", "1.44", "1.31", "1.28", "1.33", "1.29", "1.30", "1.23", "1.25"),
    "MN": ("1.16", "1.11", "1.07", "1.09", "0.97", "0.91", "0.90", "0.92", "1.53"),
    "MT": ("1.32", "1.12", "1.12", "1.12", "1.12", "1.12", "1.12", "1.12", "0.95"),
    "NM": ("0.90", "0.81", "0.73", "0.76", "0.73", "0.85", "0.87", "0.93", "0.99"),
}
# Utah's reserve factor and social contribution rate (percent), from the
# Department of Workforce Services. A new employer's basic rate is the greater
# of its industry's benefit cost rate and 1% (Utah Code 35A-4-303(5)(b)), and
# the Department of Labor's average employer rates of 0.41% to 0.68% leave the
# statewide average benefit cost rate below 1%.
UT_RESERVE_FACTOR_AND_SOCIAL_RATE = (
    ("1.00", "0.1"),
    ("1.00", "0.1"),
    ("1.00", "0.1"),
    ("1.05", "0.2"),
    ("1.15", "0.3"),
    ("1.10", "0.3"),
    ("1.10", "0.3"),
    ("1.10", "0.2"),
    ("1.10", "0.1"),
)
# Washington's history factor, from the Employment Security Department's
# new-employer pages, and the average experience and total tax rates (percent)
# from its first trust fund forecast of each year. No surviving ESD page
# states the 2020 factor; the parameter takes 90%, the factor for 2018 and 2019.
WA_HISTORY_FACTOR = (
    "0.90",
    "0.90",
    "0.90",
    "1.15",
    "1.15",
    "0.90",
    "0.90",
    "0.90",
    "1.15",
)
WA_EXPERIENCE_AND_TOTAL_RATE = (
    ("0.90", "1.07"),
    ("0.80", "0.97"),
    ("0.78", "0.94"),
    ("0.80", "1.10"),
    ("1.00", "1.34"),
    ("1.03", "1.43"),
    ("0.88", "1.33"),
    ("0.76", "1.17"),
    ("0.65", "1.08"),
)
INDUSTRY_RATE_CODES = ("LA", "MN", "MT", "NM", "UT", "WA")


def _new_employer_rate(code, year):
    # The state's new-employer rule applied to the statewide average, in
    # percent.
    i = year - FIRST_PUBLISHED_YEAR
    minimum = MINIMUM_NEW_EMPLOYER_RATE[code]
    if code == "UT":
        # The 1% basic rate times the reserve factor, to 0.01 point, plus the
        # social rate, to 0.1 point, disregarding any remaining fraction (Utah
        # Code 35A-4-303(4)(b)(i)).
        reserve_factor, social_rate = map(Decimal, UT_RESERVE_FACTOR_AND_SOCIAL_RATE[i])
        basic = (Decimal("1") * reserve_factor).quantize(Decimal("0.01"), ROUND_FLOOR)
        overall = (basic + social_rate).quantize(Decimal("0.1"), ROUND_FLOOR)
        return max(minimum, overall)
    if code == "WA":
        # The history factor times the experience rate, at least 1%, plus the
        # history factor times the social rate, each to 0.01 point (WAC
        # 192-320-025(4) and (5)).
        factor = Decimal(WA_HISTORY_FACTOR[i])
        experience, total = map(Decimal, WA_EXPERIENCE_AND_TOTAL_RATE[i])
        point = Decimal("0.01")
        experience_tax = (factor * experience).quantize(point, ROUND_HALF_UP)
        social_tax = (factor * (total - experience)).quantize(point, ROUND_HALF_UP)
        return max(minimum, experience_tax) + social_tax
    rate = max(minimum, Decimal(STATEWIDE_AVERAGE_RATE[code][i]))
    return min(rate, NM_MAXIMUM_NEW_EMPLOYER_RATE) if code == "NM" else rate


def _percent(rate):
    return Decimal(str(rate)) * 100


def test_industry_rate_defaults_follow_the_new_employer_rules():
    for year in range(FIRST_PUBLISHED_YEAR, LAST_YEAR + 1):
        for code, minimum in MINIMUM_NEW_EMPLOYER_RATE.items():
            for rate in _quarterly_rates(code, year):
                assert _percent(rate) >= minimum, (code, year)
        for code in INDUSTRY_RATE_CODES:
            for rate in _quarterly_rates(code, year):
                assert _percent(rate) == _new_employer_rate(code, year), (
                    code,
                    year,
                )


wages = st.one_of(
    st.integers(-50_000, 0).map(float),
    st.integers(0, 150_000).map(float),
)
workers = st.fixed_dictionaries(
    {
        "wages": wages,
        "raise": st.integers(0, 100_000).map(float),
        "state": st.sampled_from(CODES),
    }
)

SEED = 20261108


def _seeded_workers(per_jurisdiction=2):
    rng = np.random.default_rng(SEED)
    return [
        {
            "wages": float(rng.integers(-50_000, 150_001)),
            "raise": float(rng.integers(0, 100_001)),
            "state": code,
        }
        for code in CODES
        for _ in range(per_jurisdiction)
    ]


def _people(batch):
    # Each worker appears twice, at their wages and after their raise.
    return [
        {**worker, "wages": wages, "twin": i}
        for i, worker in enumerate(batch)
        for wages in (worker["wages"], worker["wages"] + worker["raise"])
    ]


def _situation(people):
    situation = {"people": {}, "households": {}}
    for i, person in enumerate(people):
        positive = max(person["wages"], 0)
        situation["people"][f"person_{i}"] = {
            "employment_income": {year: person["wages"] for year in SIMULATED_YEARS},
            "employer_total_taxable_earnings_for_state_unemployment_tax": {
                year: min(positive, _wage_base(person["state"], year))
                for year in SIMULATED_YEARS
            },
        }
        situation["households"][f"household_{i}"] = {
            "members": [f"person_{i}"],
            "state_code": {year: person["state"] for year in SIMULATED_YEARS},
        }
    return situation


def _calculate(sim, variable, year):
    return np.asarray(sim.calculate(variable, year), dtype=float)


def _check(batch):
    people = _people(batch)
    wages = np.array([person["wages"] for person in people])
    state = np.array([person["state"] for person in people])
    positive = np.maximum(wages, 0)
    base, raised = np.arange(0, len(people), 2), np.arange(1, len(people), 2)

    sim = Simulation(situation=_situation(people))
    for year in SIMULATED_YEARS:
        wage_base = np.array([_wage_base(code, year) for code in state])
        taxable = np.minimum(positive, wage_base)
        annual_rate = np.array([_annual_rate(code, year) for code in state])
        top_rate = np.array([max(_quarterly_rates(code, year)) for code in state])

        total = _calculate(sim, "employer_state_unemployment_tax", year)
        expected = {
            "employer_state_unemployment_tax": annual_rate * taxable,
            "nj_employer_temporary_disability_insurance_contribution": np.where(
                state == "NJ", NJ_EMPLOYER_TDI_RATE * taxable, 0
            ),
            "nj_employer_workforce_fund_contribution": np.where(
                state == "NJ", NJ_EMPLOYER_WORKFORCE_RATE * taxable, 0
            ),
            "ri_employer_job_development_fund_tax": np.where(
                state == "RI",
                RI_JDF_RATE.get(year, RI_JDF_DEFAULT_RATE) * taxable,
                0,
            ),
            "ak_employee_unemployment_insurance_contribution": np.where(
                state == "AK",
                AK_EMPLOYEE_RATE.get(year, AK_EMPLOYEE_DEFAULT_RATE) * taxable,
                0,
            ),
        }
        for variable, amount in expected.items():
            computed = (
                total
                if variable == "employer_state_unemployment_tax"
                else (_calculate(sim, variable, year))
            )
            # 4. Differential against the published tables; 8. geography for
            # the state-specific contributions, which are zero elsewhere.
            np.testing.assert_allclose(
                computed, amount, atol=TOLERANCE, rtol=0, err_msg=f"{variable} {year}"
            )
            # 5. Bounds.
            assert (computed >= 0).all(), (variable, year)
            np.testing.assert_array_equal(computed[wages <= 0], 0)
            # 6. Monotonicity.
            assert (computed[raised] >= computed[base] - TOLERANCE).all(), (
                variable,
                year,
            )
        assert (total <= top_rate * positive + TOLERANCE).all(), year

        # 8. Geography: each jurisdiction's tax is zero outside it, and the
        # jurisdiction taxes add up to the total.
        by_jurisdiction = 0
        for code in CODES:
            amount = _calculate(
                sim, f"{SLUG[code]}_employer_state_unemployment_tax", year
            )
            np.testing.assert_array_equal(amount[state != code], 0)
            by_jurisdiction = by_jurisdiction + amount
        np.testing.assert_allclose(by_jurisdiction, total, atol=TOLERANCE, rtol=0)

        # 7. Agreement of the employer-total and worker paths.
        np.testing.assert_allclose(
            _calculate(sim, "employer_total_state_unemployment_tax", year),
            total,
            atol=TOLERANCE,
            rtol=0,
            err_msg=f"employer_total_state_unemployment_tax {year}",
        )
        additional = _calculate(sim, "employer_additional_state_payroll_tax", year)
        total_additional = _calculate(
            sim, "employer_total_additional_state_payroll_tax", year
        )
        for code in ("NJ", "RI"):
            in_state = state == code
            np.testing.assert_allclose(
                total_additional[in_state],
                additional[in_state],
                atol=TOLERANCE,
                rtol=0,
                err_msg=f"employer_total_additional_state_payroll_tax {code} {year}",
            )


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(workers, min_size=1, max_size=12))
def test_employer_state_unemployment_tax_history_invariants(batch):
    _check(batch)


def test_employer_state_unemployment_tax_history_invariants_seeded_population():
    _check(_seeded_workers())
