from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class az_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arizona LIHEAP annual income limit"
    documentation = (
        "Twelve times the Appendix A monthly gross income limit for the "
        "eligible household size: the greater of 60% of the state median income "
        "and 150% of the federal poverty guideline, each floored to whole "
        "monthly dollars."
    )
    reference = (
        # Section VI.A.6.c.i (page 8) and Appendix A (page 37).
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=37",
        # Section 2.1 (page 9).
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=9",
        "https://liheapch.acf.gov/profiles/povertytables/FY2026/azsmi.htm",
        "https://liheapch.acf.gov/profiles/povertytables/FY2026/popstate.htm",
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.eligibility
        size = spm_unit("az_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        state_group = spm_unit.household("state_group_str", period)
        # Section VI.A.6.c.i: "Gross Income must be at or below the greater of:
        # A) 60% of the SMI; or B) 150% of the FPL." Appendix A prints the
        # FFY2026 monthly result for sizes 1 to 12 plus $687 per additional
        # person. Its SMI arm reproduces only when the four-person 60% amount is
        # floored first (64,789 from 107,983), then the size-adjusted annual
        # amount, then the monthly amount; this is a reconciled numerical
        # pattern, not an explicit rounding rule.
        smi = parameters(period).gov.hhs.smi
        four_person_limit = np.floor(smi.amount[state] * p.smi_rate)
        adjustment = smi.household_size_adjustment
        threshold = smi.additional_person_threshold
        size_share = (
            adjustment.first_person
            + adjustment.second_to_sixth_person * clip(size - 1, 0, threshold - 1)
            + adjustment.additional_person * max_(size - threshold, 0)
        )
        smi_monthly = np.floor(
            np.floor(four_person_limit * size_share) / MONTHS_IN_YEAR
        )
        # The FPL arm uses the guideline in force when the season's limits were
        # set (the 2025 guideline for FFY2026) and floors the monthly amount.
        # Appendix A's "EACH ADDL OVER 12 +$687" is the floored monthly value of
        # 150% of the additional-person guideline, applied beyond the table.
        capped_size = clip(size, 1, p.max_table_size)
        guideline = fpg(
            capped_size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        additional_guideline = (
            fpg(
                capped_size + 1,
                state_group,
                period,
                parameters,
                year_lag=p.fpg_year_lag,
            )
            - guideline
        )
        fpg_monthly = np.floor(p.fpg_rate * guideline / MONTHS_IN_YEAR)
        increment = np.floor(p.fpg_rate * additional_guideline / MONTHS_IN_YEAR)
        additional_people = max_(size - p.max_table_size, 0)
        fpg_monthly = fpg_monthly + additional_people * increment
        monthly_limit = max_(smi_monthly, fpg_monthly)
        return where(size > 0, monthly_limit * MONTHS_IN_YEAR, 0)
