from policyengine_us.model_api import *


class wa_snap_bbce_gross_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington SNAP BBCE gross income limit"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Washington's Basic Food broad-based categorical eligibility "
        "monthly gross income limit."
    )
    reference = "https://app.leg.wa.gov/WAC/default.aspx?cite=388-414-0001"
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # WAC 388-414-0001(2)(a)(ii): Washington applies the federal
        # poverty guidelines published for the current year beginning
        # each April 1, unlike the federal SNAP tests, which follow the
        # October fiscal-year schedule.
        guideline_year = (
            period.start.year if period.start.month >= 4 else period.start.year - 1
        )
        p_fpg = parameters(f"{guideline_year}-01-01").gov.hhs.fpg
        p1 = p_fpg.first_person["CONTIGUOUS_US"]
        pn = p_fpg.additional_person["CONTIGUOUS_US"]
        n = spm_unit("snap_unit_size", period)
        annual_fpg = p1 + pn * (n - 1)
        rate = parameters(period).gov.hhs.tanf.non_cash.income_limit.gross.WA
        # DSHS publishes the monthly standards rounded to the closest
        # whole dollar.
        return round_(annual_fpg * rate / MONTHS_IN_YEAR)
