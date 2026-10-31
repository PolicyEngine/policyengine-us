"""CMS cumulative CPI indexing and projection of federal spousal standards.

These parameter-tree checks cannot use the YAML policy runner: they exercise
projection coverage, published precedence and forecast normalization without
building additional simulations. Published values are from the chart page of
CMS's SSI and spousal impoverishment bulletins for 2021, 2022, 2025 and
2026; statute 42 USC 1396r-5(g) sets the September 1988 reference period.

The 2020 bulletin publishes a 114.4% cumulative increase, whereas BLS's
September 2019 index (256.759) over September 1988 (119.8) gives 114.3%
after rounding. CMS does not explain the discrepancy in that bulletin.
Keep its published amounts as explicit values rather than deriving 2020
with a special-case rule; projections begin after the final published year.
"""

import pytest

from policyengine_core.parameters import ParameterNode
from policyengine_us.parameters.uprating_extensions import (
    extend_medicaid_spousal_impoverishment_standards,
    get_cms_spousal_impoverishment_multiplier,
)
from policyengine_us.system import system

FEDERAL = (
    system.parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal
)
PUBLISHED_STANDARDS = {
    # year: (cumulative CPI increase %, CSRA minimum, CSRA maximum, MMMNA maximum)
    2021: (117.3, 26_076, 130_380, 3_259.5),
    2022: (129.0, 27_480, 137_400, 3_435),
    2025: (163.2, 31_584, 157_920, 3_948),
    2026: (171.1, 32_532, 162_660, 4_066.5),
}


@pytest.mark.parametrize("year, published", PUBLISHED_STANDARDS.items())
def test_cumulative_indexing_reproduces_cms(year, published):
    percentage, minimum, maximum, mmmna = published
    multiplier = get_cms_spousal_impoverishment_multiplier(system.parameters, year)
    assert multiplier == pytest.approx(1 + percentage / 100)
    date = f"{year}-01-01"
    assert FEDERAL.csra.minimum_base(date) * multiplier == pytest.approx(minimum)
    assert FEDERAL.csra.maximum_base(date) * multiplier == pytest.approx(maximum)
    assert FEDERAL.mmmna.maximum_base(date) * multiplier == pytest.approx(mmmna)


def test_published_and_projected_standards_are_january_parameters():
    assert FEDERAL.csra.minimum("2026-01-01") == 32_532
    assert FEDERAL.csra.maximum("2026-01-01") == 162_660
    assert FEDERAL.mmmna.maximum("2026-01-01") == 4_066.5
    for year in range(2027, 2041):
        multiplier = get_cms_spousal_impoverishment_multiplier(system.parameters, year)
        for parameter, statutory_base in (
            (FEDERAL.csra.minimum, FEDERAL.csra.minimum_base),
            (FEDERAL.csra.maximum, FEDERAL.csra.maximum_base),
            (FEDERAL.mmmna.maximum, FEDERAL.mmmna.maximum_base),
        ):
            current = parameter(f"{year}-01-01")
            assert current == pytest.approx(
                statutory_base(f"{year}-01-01") * multiplier
            )
            for month in ("02", "07", "12"):
                assert parameter(f"{year}-{month}-01") == current
    assert FEDERAL.csra.minimum("2027-01-01") > FEDERAL.csra.minimum("2026-01-01")


def _parameters(published_maximum=False, minimum_base=12_000):
    maximum = {"2026-01-01": 162_660}
    if published_maximum:
        maximum["2027-01-01"] = 200_000
    return ParameterNode(
        data={
            "gov": {
                "hhs": {
                    "medicaid": {
                        "eligibility": {
                            "long_term_care": {
                                "financial": {
                                    "federal": {
                                        "indexing": {
                                            "base_year": {
                                                "values": {"1989-01-01": 1988}
                                            },
                                            "reference_month": {
                                                "values": {"1989-01-01": 9}
                                            },
                                            "percentage_rounding_interval": {
                                                "values": {"1989-01-01": 0.1}
                                            },
                                        },
                                        "csra": {
                                            "minimum": {
                                                "values": {"2026-01-01": 32_532}
                                            },
                                            "maximum": {"values": maximum},
                                            "minimum_base": {
                                                "values": {"1989-01-01": minimum_base}
                                            },
                                            "maximum_base": {
                                                "values": {"1989-01-01": 60_000}
                                            },
                                        },
                                        "mmmna": {
                                            "maximum": {
                                                "values": {"2026-01-01": 4_066.5}
                                            },
                                            "maximum_base": {
                                                "values": {"1989-01-01": 1_500}
                                            },
                                        },
                                    }
                                }
                            }
                        }
                    }
                },
                "bls": {
                    "cpi": {
                        "cpi_u_nsa_september": {
                            "values": {"1988-09-01": 119.8, "2025-09-01": 324.8}
                        },
                        # A different SA level at the common September must
                        # not become an inflation adjustment. The forecast
                        # rises 4% a year regardless of this level difference.
                        "cpi_u": {
                            "values": {
                                "2025-09-01": 300,
                                "2026-09-01": 312,
                                "2027-09-01": 324.48,
                            }
                        },
                    }
                },
            }
        }
    )


def test_projection_normalizes_to_the_last_published_nsa_level():
    parameters = _parameters()
    # 324.8 x (312 / 300) / 119.8 = 2.81963272...; CMS rounds the
    # cumulative increase to 182.0%, giving the multiplier 2.820.
    assert get_cms_spousal_impoverishment_multiplier(parameters, 2027) == 2.820
    # Published 2026 uses NSA 324.8 directly, not the SA level of 300.
    assert get_cms_spousal_impoverishment_multiplier(parameters, 2026) == 2.711
    extend_medicaid_spousal_impoverishment_standards(parameters, end_year=2030)
    federal = parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal
    assert federal.csra.minimum("2027-01-01") == 33_840
    assert federal.csra.maximum("2027-01-01") == 169_200
    assert federal.mmmna.maximum("2027-01-01") == 4_230
    # Chaining the rounded 2026 standard by 4% would produce $33,833.28.
    assert federal.csra.minimum("2027-01-01") != 32_532 * 1.04


@pytest.mark.parametrize("published_maximum", [False, True])
def test_each_standard_respects_its_own_published_coverage(published_maximum):
    parameters = _parameters(published_maximum)
    extend_medicaid_spousal_impoverishment_standards(parameters, end_year=2030)
    federal = parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal
    expected_maximum = 200_000 if published_maximum else 169_200
    assert federal.csra.maximum("2027-01-01") == expected_maximum
    assert federal.csra.minimum("2027-01-01") == 33_840
    assert federal.mmmna.maximum("2027-01-01") == 4_230
    assert federal.csra.maximum("2028-01-01") == 175_920


def test_historical_published_standards_are_preserved():
    parameters = _parameters()
    federal = parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal
    # CMS cib062420-new.pdf p.2: this published year differs from the
    # rounded raw-index ratio and must remain authoritative for its year.
    published = (
        (federal.csra.minimum, 25_728),
        (federal.csra.maximum, 128_640),
        (federal.mmmna.maximum, 3_216),
    )
    for parameter, value in published:
        parameter.update(period="year:2020-01-01:1", value=value)
    extend_medicaid_spousal_impoverishment_standards(parameters, end_year=2030)
    for parameter, value in published:
        assert parameter("2020-01-01") == value


def test_projection_reads_reformed_statutory_bases():
    parameters = _parameters(minimum_base=13_000)
    extend_medicaid_spousal_impoverishment_standards(parameters, end_year=2027)
    federal = parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal
    assert federal.csra.minimum("2027-01-01") == 36_660
    assert federal.csra.maximum("2027-01-01") == 169_200
