"""Invariants for Hawaii's unemployment insurance wage base and new-employer rate.

HRS 383-61(b) sets the taxable wage base at the average annual wage for the
four quarters ending June 30 of the preceding year, rounded to the nearest
hundred dollars. Subsections (c) and (d) set 1988, 1991 and 2008 to 2011
otherwise, and subsections (d) and (f) keep the base at or above the federal
unemployment tax base. HRS 392-43(b)(2) caps temporary disability insurance
benefits from the same average annual wage, so the Department of Labor and
Industrial Relations (DLIR) prints it, to the cent, in each year's TDI notice.

The tables below copy DLIR's publications, not the parameters:

- WAGE_BASE: the taxable wage bases in DLIR's December 2019 trust fund
  evaluation (Appendix B, 1970 to 2020) and on its tax rate schedule page
  (2020 to 2026);
- RESERVE_RATIO and SCHEDULE: the evaluation's ratio of the current to the
  adequate reserve fund and the rate schedule in effect, for the rate years
  that the tests below use, with the schedule page's schedules from 2021;
- AVERAGE_ANNUAL_WAGE: the average annual wage in DLIR's TDI notices for 2004
  to 2026.

The tests read only parameters, so they build no simulation:

1. Publication: on every date from 1970 through 2026, the wage base equals
   DLIR's base for that year, apart from 2010 (see 4). A sweep checks the
   first and last day of each year, and Hypothesis draws other dates.
2. Dates: every stored wage base starts on January 1.
3. Formula: in each year that the notices cover and that subsections (c) and
   (d) leave alone, the base equals the average annual wage rounded half up
   to the nearest hundred dollars.
4. Special years: 1991 is $7,000, and 2008 and 2009 are $13,000 with the fund
   at or above its adequate reserve (subsection (c)). Subsection (d) sets 1988
   at 50% of the average annual wage for a reserve ratio of 1.2 or more, and
   DLIR's $8,700 doubles to an average between the 1987 and 1989 bases. 2010
   and 2011 take 90% of the average annual wage, which subsection (b) rounds
   to the nearest hundred dollars. That gives $34,920 for 2010, which the
   parameter holds. DLIR's $34,900 also rounds the 90% figure, an intended
   difference that source_conflicts/candidates.yaml records as
   us-hi:ui-taxable-wage-base-2010-rounding.
5. Federal floor: the base never falls below the highest federal unemployment
   tax base enacted by its year, and 1991 meets the $7,000 federal base.
6. New employers: from 2015, the default rate equals the rate that HRS
   383-68 sets for a .0000 reserve ratio on the year's schedule, as HRS
   383-66(a)(2) assigns to new employers.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us.system import system

HI = system.parameters.gov.states.hi.tax.payroll.unemployment
FUTA = system.parameters.gov.irs.payroll.federal_unemployment

# DLIR, Annual Evaluation of the Unemployment Compensation Trust Fund, December
# 2019, Appendix B, Total and Taxable Wages (1970 to 2020), and DLIR, Tax Rate
# Schedule and Weekly Benefit Amount (2020 to 2026).
WAGE_BASE = {
    1970: 5_500,
    1971: 6_000,
    1972: 6_300,
    1973: 6_500,
    1974: 6_800,
    1975: 7_300,
    1976: 7_800,
    1977: 9_300,
    1978: 9_800,
    1979: 10_400,
    1980: 11_200,
    1981: 12_200,
    1982: 13_100,
    1983: 13_800,
    1984: 14_600,
    1985: 15_100,
    1986: 15_600,
    1987: 16_500,
    1988: 8_700,
    1989: 18_600,
    1990: 19_900,
    1991: 7_000,
    1992: 22_700,
    1993: 23_900,
    1994: 25_000,
    1995: 25_500,
    1996: 25_800,
    1997: 26_000,
    1998: 26_400,
    1999: 27_000,
    2000: 27_500,
    2001: 28_400,
    2002: 29_300,
    2003: 30_200,
    2004: 31_000,
    2005: 32_300,
    2006: 34_000,
    2007: 35_300,
    2008: 13_000,
    2009: 13_000,
    2010: 34_900,
    2011: 34_200,
    2012: 38_800,
    2013: 39_600,
    2014: 40_400,
    2015: 40_900,
    2016: 42_200,
    2017: 44_000,
    2018: 45_900,
    2019: 46_800,
    2020: 48_100,
    2021: 47_400,
    2022: 51_600,
    2023: 56_700,
    2024: 59_100,
    2025: 62_000,
    2026: 64_500,
}
FIRST_YEAR = min(WAGE_BASE)
LAST_YEAR = max(WAGE_BASE)

# HRS 383-61(c) sets 2010 at 90% of the rounded average annual wage; DLIR's
# table rounds that figure to $34,900.
STATUTE_READING = {2010: 34_920}

# The evaluation's Appendix B, Ratio of Current to Adequate Reserve Fund. The
# current reserve fund is the trust fund's assets on November 30 of the year
# before the rate year.
RESERVE_RATIO = {1988: 2.08, 2008: 2.25, 2009: 1.77}

# Rate schedule in effect: the evaluation's Appendix B through 2020, HRS
# 383-68(c) for 2021 and 2022, and DLIR's schedule page from 2023.
SCHEDULE = {
    2015: "D",
    2016: "C",
    2017: "C",
    2018: "C",
    2019: "C",
    2020: "C",
    2021: "D",
    2022: "D",
    2023: "F",
    2024: "D",
    2025: "C",
    2026: "C",
}

# HRS 383-68(d), contribution rates for a reserve ratio of .0000 to .0299.
ZERO_RESERVE_RATE = {
    "A": "0.017",
    "B": "0.019",
    "C": "0.024",
    "D": "0.030",
    "E": "0.034",
    "F": "0.040",
    "G": "0.046",
    "H": "0.052",
}

# Average annual wage under HRS 383-61(b), from DLIR Disability Compensation
# Division notices of the TDI maximum weekly wage base, with each notice.
AVERAGE_ANNUAL_WAGE = {
    2004: (
        "30972.13",
        "https://web.archive.org/web/20050226051453/http://hawaii.gov:80/labor/dcd/pdf/TDI/2004%20TDI%20Wage%20Base.pdf",
    ),
    2005: (
        "32336.24",
        "https://web.archive.org/web/20050226052914/http://hawaii.gov:80/labor/dcd/pdf/general/2005_WAGE_BASE.pdf",
    ),
    2006: (
        "34023.65",
        "https://web.archive.org/web/20060227223955/http://hawaii.gov:80/labor/dcd/pdf/general/2006_WAGE_BASE.pdf",
    ),
    2007: (
        "35250.68",
        "https://web.archive.org/web/20080719002041/http://hawaii.gov/labor/dcd/PDF/general/2007_Wage_Base_12-1-06.pdf",
    ),
    2008: (
        "36209.17",
        "https://web.archive.org/web/20080724052848/http://hawaii.gov/labor/dcd/PDF/general/WAGE%20BASE-2008%20%28PDF%29.pdf",
    ),
    2009: (
        "37718.93",
        "https://web.archive.org/web/20121025001236/http://hawaii.gov/labor/dcd/PDF/general/2009%20Wage%20Base.pdf",
    ),
    2010: (
        "38750.59",
        "https://web.archive.org/web/20101215215838/http://hawaii.gov/labor/dcd/PDF/general/2010%20Wage%20Base.pdf",
    ),
    2011: (
        "38002.62",
        "https://web.archive.org/web/20101215215837/http://hawaii.gov/labor/dcd/PDF/general/2011%20Wage%20Base.pdf",
    ),
    2012: (
        "38818.32",
        "https://web.archive.org/web/20121024102028/http://hawaii.gov/labor/dcd/PDF/general/2012%20Wage%20Base.pdf",
    ),
    2013: (
        "39613.57",
        "https://web.archive.org/web/20141030021517/http://labor.hawaii.gov/dcd/files/2013/01/Old-Wage-Base.pdf",
    ),
    2014: (
        "40398.56",
        "https://web.archive.org/web/20141030011206/http://labor.hawaii.gov/dcd/files/2013/01/New-Wage-Base.pdf",
    ),
    2015: (
        "40879.44",
        "https://web.archive.org/web/20160824005208/http://labor.hawaii.gov:80/dcd/files/2013/01/2015-Wage-Base.pdf",
    ),
    2016: (
        "42217.41",
        "https://web.archive.org/web/20160706000230/http://labor.hawaii.gov:80/dcd/files/2014/11/2016.pdf",
    ),
    2017: (
        "43976.82",
        "https://web.archive.org/web/20171101222709/https://labor.hawaii.gov/dcd/files/2013/01/17Wbase.pdf",
    ),
    2018: (
        "45924.45",
        "https://labor.hawaii.gov/dcd/files/2017/11/2018.pdf",
    ),
    2019: (
        "46760.69",
        "https://labor.hawaii.gov/dcd/files/2018/11/2019wagebase.pdf",
    ),
    2020: (
        "48108.20",
        "https://web.archive.org/web/20201017202041/https://labor.hawaii.gov/dcd/files/2019/11/newWBA.pdf",
    ),
    2021: (
        "47397.51",
        "https://web.archive.org/web/20201204141806/https://labor.hawaii.gov/dcd/files/2019/11/newWBA.pdf",
    ),
    2022: (
        "51582.77",
        "https://web.archive.org/web/20220819164238/https://labor.hawaii.gov/dcd/files/2019/11/newWBA.pdf",
    ),
    2023: (
        "56662.05",
        "https://web.archive.org/web/20230306111219/https://labor.hawaii.gov/dcd/files/2019/11/newWBA.pdf",
    ),
    2024: (
        "59081.47",
        "https://labor.hawaii.gov/dcd/files/2023/11/2024-Max-Weekly-Wage-Base-Weekly-Benefit-Amount.pdf",
    ),
    2025: (
        "61958.21",
        "https://labor.hawaii.gov/dcd/files/2023/05/2025-Max-Weekly-Wage-Base-Rev-2025.03.pdf",
    ),
    2026: (
        "64471.82",
        "https://labor.hawaii.gov/dcd/files/2025/12/2026-Maximum-Weekly-Wage-Base.pdf",
    ),
}
SPECIAL_YEARS = {1988, 1991, 2008, 2009, 2010, 2011}


def _base(year):
    return HI.taxable_wage_base(f"{year}-01-01")


def _expected(year):
    return STATUTE_READING.get(year, WAGE_BASE[year])


def _round_to_hundred(amount):
    return int(Decimal(amount).quantize(Decimal("1E2"), rounding=ROUND_HALF_UP))


def _average_annual_wage(year):
    # HRS 383-61(b): the quotient, rounded to the nearest hundred dollars.
    return _round_to_hundred(AVERAGE_ANNUAL_WAGE[year][0])


def _subsection_d_share(ratio):
    # HRS 383-61(d)(1) to (3), for 1988 only.
    if ratio <= 0.8:
        return Decimal("1")
    if ratio < 1.2:
        return Decimal("0.75")
    return Decimal("0.5")


def _highest_federal_base_enacted(year):
    # 26 U.S.C. 3306(b)(1). Public Law 91-373 (August 10, 1970) raised the base
    # from $3,000 to $4,200, Public Law 94-566 (October 20, 1976) to $6,000,
    # and Public Law 97-248 to $7,000 for remuneration paid after 1982.
    if year < 1976:
        return 4_200
    if year < 1983:
        return 6_000
    return FUTA.taxable_wage_base(f"{year}-01-01")


def test_tables_cover_every_year():
    assert sorted(WAGE_BASE) == list(range(FIRST_YEAR, LAST_YEAR + 1))
    assert sorted(AVERAGE_ANNUAL_WAGE) == list(range(2004, LAST_YEAR + 1))
    assert sorted(SCHEDULE) == list(range(2015, LAST_YEAR + 1))


def test_wage_base_equals_the_published_base_on_the_first_and_last_day():
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        for day in (f"{year}-01-01", f"{year}-12-31"):
            assert HI.taxable_wage_base(day) == _expected(year), day


@settings(max_examples=200, deadline=None)
@given(st.dates(min_value=date(FIRST_YEAR, 1, 1), max_value=date(LAST_YEAR, 12, 31)))
def test_wage_base_equals_the_published_base_on_any_date(day):
    assert HI.taxable_wage_base(day.isoformat()) == _expected(day.year)


def test_stored_wage_bases_start_on_january_first():
    stored = [value.instant_str for value in HI.taxable_wage_base.values_list]
    assert min(stored) == f"{FIRST_YEAR}-01-01"
    assert all(instant.endswith("-01-01") for instant in stored), stored


def test_wage_base_follows_the_average_annual_wage():
    for year in sorted(set(AVERAGE_ANNUAL_WAGE) - SPECIAL_YEARS):
        assert _base(year) == _average_annual_wage(year), year
        assert WAGE_BASE[year] == _average_annual_wage(year), year


def test_special_years_follow_subsections_c_and_d():
    assert _base(1991) == 7_000
    for year in (2008, 2009):
        assert RESERVE_RATIO[year] >= 1, year
        assert _base(year) == 13_000, year

    share = _subsection_d_share(RESERVE_RATIO[1988])
    assert share == Decimal("0.5")
    assert _base(1987) < Decimal(_base(1988)) / share < _base(1989)

    for year in (2010, 2011):
        ninety_percent = Decimal("0.9") * _average_annual_wage(year)
        assert _base(year) == ninety_percent, year
        assert WAGE_BASE[year] == _round_to_hundred(ninety_percent), year
    assert _base(2010) == 34_920
    assert WAGE_BASE[2010] == 34_900


def test_wage_base_stays_at_or_above_the_federal_base():
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        assert _base(year) >= _highest_federal_base_enacted(year), year
    assert _base(1991) == _highest_federal_base_enacted(1991) == 7_000


def test_new_employer_rate_is_the_zero_reserve_rate_of_the_schedule():
    for year, schedule in SCHEDULE.items():
        for day in (f"{year}-01-01", f"{year}-12-31"):
            rate = Decimal(str(HI.default_rate(day)))
            assert rate == Decimal(ZERO_RESERVE_RATE[schedule]), day
