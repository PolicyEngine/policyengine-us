from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class co_leap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Colorado LEAP annual income limit"
    defined_for = StateCode.CO
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=4",
    )

    def formula(spm_unit, period, parameters):
        gov = parameters(period).gov
        leap = gov.states.co.cdhs.leap
        p = leap.income
        size = spm_unit("co_leap_household_size", period)
        capped_size = min_(size, p.additional_person_threshold)
        state = spm_unit.household("state_code_str", period)
        monthly = np.floor(
            liheap_smi_limit(capped_size, state, p.smi_rate, period, parameters)
            / MONTHS_IN_YEAR
        )
        extra = max_(size - p.additional_person_threshold, 0)
        # Flooring reproduces all eight FY2026 published SMI rows; the
        # independently printed increment governs additional members.
        annual_limit = (monthly + extra * p.additional_person_amount) * MONTHS_IN_YEAR
        # 42 U.S.C. 8624(b)(2)(B) pays no household above the greater of 60% of SMI
        # and 150% of the guideline. The printed FY2026 increment stays within that,
        # but it can overshoot in a year with a lower SMI.
        ceiling = max_(
            liheap_smi_limit(size, state, gov.hhs.liheap.smi_limit, period, parameters),
            gov.hhs.liheap.fpg_limit
            * fpg(
                size,
                spm_unit.household("state_group_str", period),
                period,
                parameters,
                year_lag=leap.payment.fpg_year_lag,
            ),
        )
        return where(size > 0, min_(annual_limit, ceiling), 0)
