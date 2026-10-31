"""Full earnings histories from SSA's published 2027 retirement examples.

Frozen source inputs were retrieved on 2026-10-31. The calculator receives
annual nominal earnings, annual caps, and exact NAWI observations rather than
a supplied AIME or a pre-indexed total. SSA displays its indexed annual amounts
as whole dollars; the history ledger retains the required cents.

Earnings, caps, and displayed indexed amounts:
https://www.ssa.gov/OACT/ProgData/retirebenefit1.html
Eligibility-year bend points and initial PIAs:
https://www.ssa.gov/OACT/ProgData/retirebenefit2.html
Exact national average wage index observations:
https://www.ssa.gov/OACT/COLA/AWI.html
"""

from datetime import date
from decimal import Decimal

import pytest

from policyengine_us.tools.social_security.cola import ColaEvent
from policyengine_us.tools.social_security.history import (
    EarningsHistory,
    EarningsRecord,
    HistoryParameters,
    compute_history,
    compute_history_pia,
)
from policyengine_us.tools.social_security.household import (
    SuppliedRecord,
    calculate_year,
)


# year, case-A nominal wages, case-B nominal wages (= annual ordinary cap),
# displayed indexed earnings for A and B, and exact NAWI. No 2026 NAWI is
# needed: both cases retain their age-60 year and all later years at face value.
SSA_ROWS = """
1987 17229 43800 68069 132230 18426.51
1988 18134 45000 68282 129476 19334.04
1989 18912 48000 68499 132847 20099.55
1990 19847 51300 68712 135712 21027.98
1991 20651 53400 68927 136192 21811.60
1992 21783 55500 69142 134612 22935.42
1993 22038 57600 69355 138514 23132.67
1994 22700 60600 69571 141920 23753.53
1995 23683 61200 69787 137801 24705.66
1996 24917 62700 70000 134596 25913.90
1997 26452 65400 70215 132652 27426.00
1998 27922 68400 70431 131837 28861.44
1999 29567 72600 70643 132545 30469.84
2000 31297 76200 70858 131828 32154.82
2001 32141 80400 71073 135853 32921.92
2002 32561 84900 71287 142032 33252.09
2003 33458 87000 71503 142072 34064.95
2004 35118 87900 71717 137166 35648.55
2005 36512 90000 71932 135485 36952.94
2006 38305 94200 72148 135576 38651.41
2007 40162 97500 72362 134234 40405.48
2008 41208 102000 72577 137272 41334.97
2009 40706 106800 72790 145932 40711.61
2010 41791 106800 73005 142563 41673.83
2011 43228 106800 73221 138231 42979.61
2012 44708 110100 73435 138188 44321.67
2013 45412 113700 73650 140905 44888.16
2014 47161 117000 73865 140024 46481.52
2015 48943 118500 74078 137051 48098.63
2016 49640 118500 74294 135520 48642.15
2017 51503 127200 74509 140614 50321.89
2018 53523 128400 74723 136976 52145.80
2019 55688 132900 74937 136655 54099.99
2020 57426 137700 75153 137700 55628.60
2021 62711 142800 75367 142800 60575.07
2022 66232 147000 75581 147000 63795.13
2023 69364 160200 75797 160200 66621.80
2024 72927 168600 76011 168600 69846.57
2025 76226 176100 76226 176100 72800.33
2026 79009 184500 79009 184500 -
"""


@pytest.mark.parametrize(
    "case,birth_year,eligibility,bends,expected_aime,expected_pia",
    [
        ("A", 1965, 2027, (1340, 8077), 6072, "2720.20"),
        ("B", 1960, 2022, (1024, 6172), 11843, "3419.60"),
    ],
)
def test_ssa_published_full_earnings_history(
    case, birth_year, eligibility, bends, expected_aime, expected_pia
):
    rows = [line.split() for line in SSA_ROWS.strip().splitlines()]
    wages_column = 1 if case == "A" else 2
    indexed_column = 3 if case == "A" else 4
    history = EarningsHistory(
        first_year=1987,
        records=tuple(
            EarningsRecord(int(row[0]), Decimal(row[wages_column]), 0) for row in rows
        ),
        certified_zero_before_first_year=True,
    )
    frozen_parameters = HistoryParameters(
        wage_base={int(row[0]): Decimal(row[2]) for row in rows},
        nawi={int(row[0]): Decimal(row[5]) for row in rows if row[5] != "-"},
    )
    calculation = compute_history(
        history, eligibility, 2027, frozen_parameters, birth_year=birth_year
    )
    assert calculation.aime == expected_aime
    assert compute_history_pia(calculation, bend_points=bends) == Decimal(expected_pia)
    assert len(calculation.ledger) == 40
    for annual, source in zip(calculation.ledger, rows, strict=True):
        assert annual.year == int(source[0])
        assert annual.ordinary_covered == Decimal(source[wages_column])
        # The source prints whole dollars; preserve the cents in production.
        assert abs(annual.indexed_ordinary - Decimal(source[indexed_column])) < 1
        if annual.year >= eligibility - 2:
            assert annual.indexed_ordinary == annual.ordinary_covered
    # Case B includes five years after its eligibility year; these must remain
    # available through Q-1 rather than stopping the history at age 62.
    assert calculation.ledger[-1].year == 2026
    if case == "B":
        # The same retirebenefit2 example publishes these December-effective
        # COLAs, its resulting PIA $4,187.40, and the FRA payment $4,187.
        cola_events = tuple(
            ColaEvent(f"{year}-12", f"{year + 1}-01", Decimal(rate))
            for year, rate in zip(
                range(2022, 2027), (".087", ".032", ".025", ".028", ".036"), strict=True
            )
        )
        record = SuppliedRecord(
            source="history",
            worker_id="ssa-case-b",
            birth_date=date(1960, 1, 2),
            entitlement_month="2027-01",
            insured=True,
            eligibility_year=2022,
            history=history,
            history_parameters=frozen_parameters,
            no_special_monthly_test=True,
            no_prior_withholding_adjustment=True,
            earnings_test_no_trigger=True,
        )
        benefit = calculate_year(
            record, 2027, bend_points=bends, cola_events=cola_events
        )
        january = next(
            row for row in benefit.ledger if row.entitlement_month == "2027-01"
        )
        assert january.eligibility_pia == Decimal("3419.6")
        assert january.cola_pia == Decimal("4187.4")
        assert january.payable_benefit == 4187
        assert benefit.entitlement_total == 4187 * 12
        assert benefit.payment_total == 4187 * 11
