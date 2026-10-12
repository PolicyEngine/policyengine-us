from policyengine_us.model_api import *


class in_tanf_countable_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF countable income eligible"
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-1",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-1-1.7",
        "https://www.in.gov/fssa/dfr/files/3000.pdf#page=4",
        "https://www.in.gov/fssa/dfr/files/3000.pdf#page=5",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.eligibility
        countable = spm_unit("in_tanf_countable_income_for_eligibility", period)
        fpg = spm_unit("in_tanf_fpg", period)

        # Continuing/enrolled recipients: countable net income below 100% FPG
        # (470 IAC 10.3-4-1; FSSA 3010.15.05).
        continuing_eligible = countable < fpg * p.continuing.fpg_rate

        # Initial applicants. The net income standard is the standard of need
        # before 2025-07-01 (maximum grant rate of 0) and the maximum grant
        # from 2025-07-01 (FSSA 3010.15.00). From 2025-07-01 there is also a
        # gross income screen at 35% FPG, rising to 50% after June 30, 2027
        # (IC 12-14-1-1.7); before then the screen is inactive.
        standard_of_need = spm_unit("in_tanf_payment_standard", period)
        maximum_grant = spm_unit("in_tanf_maximum_benefit", period)
        grant_rate = p.initial.net_income.maximum_grant_rate
        net_threshold = where(
            grant_rate > 0, maximum_grant * grant_rate, standard_of_need
        )
        gross_income = spm_unit("in_tanf_gross_income", period)
        gross_threshold = spm_unit("in_tanf_initial_gross_income_standard", period)
        initial_eligible = (countable < net_threshold) & (
            gross_income < gross_threshold
        )

        is_enrolled = spm_unit("is_tanf_enrolled", period)
        return where(is_enrolled, continuing_eligible, initial_eligible)
