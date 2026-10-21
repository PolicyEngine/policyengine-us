from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ca_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "California LIHEAP annualized income limit"
    defined_for = StateCode.CA
    # PDF pages 9,184
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=9"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.income
        p_smi = parameters(period).gov.hhs.smi
        size = spm_unit("ca_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        four_person_smi = p_smi.amount[state]
        rounded_base = (
            np.floor(four_person_smi * p.smi_rate / p.smi_annual_rounding_increment)
            * p.smi_annual_rounding_increment
        )
        capped_size = clip(size, 1, p.smi_rounding_size_limit)
        adjusted_base = smi(capped_size, state, period, parameters) * (
            rounded_base / four_person_smi
        )
        rounded_annual = (
            np.floor(adjusted_base / p.smi_annual_rounding_increment)
            * p.smi_annual_rounding_increment
        )
        extra_people = max_(size - p.smi_rounding_size_limit, 0)
        annual_increment = (
            rounded_base * p_smi.household_size_adjustment.additional_person
        )
        monthly = (
            rounded_annual / MONTHS_IN_YEAR
            + extra_people * annual_increment / MONTHS_IN_YEAR
        )
        # This inferred two-stage rounding reproduces all 25 FY2026 rows;
        # the source does not prescribe the size-12 switch or an extension.
        rounded_monthly = (
            np.floor(monthly / p.monthly_rounding_increment)
            * p.monthly_rounding_increment
        )
        return rounded_monthly * MONTHS_IN_YEAR
