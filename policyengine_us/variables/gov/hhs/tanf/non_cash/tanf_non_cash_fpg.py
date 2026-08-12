from policyengine_us.model_api import *


class tanf_non_cash_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "TANF non-cash federal poverty guideline"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Monthly federal poverty guideline underlying the TANF non-cash "
        "(SNAP BBCE) income standards, using the guideline vintage each "
        "state's standard is based on in this month."
    )

    def formula(spm_unit, period, parameters):
        # States re-base their BBCE standards to a new year's poverty
        # guidelines on their own schedule: most follow the federal
        # October fiscal-year cycle, while e.g. Washington re-bases each
        # April 1 (WAC 388-414-0001(2)(a)(ii)). The month each state
        # starts using the current calendar year's guidelines is a
        # parameter; before it, the prior year's guidelines apply.
        state = spm_unit.household("state_code_str", period.this_year)
        start_month = parameters(
            period
        ).gov.hhs.tanf.non_cash.income_limit.fpg_year_start_month[state]
        n = spm_unit("snap_unit_size", period)
        state_group = spm_unit.household("state_group_str", period.this_year)
        year = period.start.year

        # snap_fpg encodes the same guideline arithmetic on the fixed
        # federal October cycle; this variable generalizes it with a
        # per-state cutover month. Keep the two in sync.
        def monthly_fpg(guideline_year):
            p_fpg = parameters(f"{guideline_year}-01-01").gov.hhs.fpg
            p1 = p_fpg.first_person[state_group]
            pn = p_fpg.additional_person[state_group]
            return (p1 + pn * (n - 1)) / MONTHS_IN_YEAR

        return where(
            period.start.month >= start_month,
            monthly_fpg(year),
            monthly_fpg(year - 1),
        )
