from policyengine_us.model_api import *


class ca_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "California LIHEAP annualized countable income"
    defined_for = StateCode.CA
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=7,229,230,231,232,233,234,235,236,237,238,239,240,243,244,245,246,247"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.income
        gross = add(
            spm_unit,
            period,
            ["ca_liheap_countable_earned_income"] + p.unearned_sources,
        )
        support_paid = add(spm_unit, period, p.support_deductions)
        person = spm_unit.members
        direct_premiums = person("health_insurance_premiums", period)
        premiums_without_part_b = person(
            "health_insurance_premiums_without_medicare_part_b", period
        )
        # Use reported allowable non-Medicare medical premiums as a proxy.
        # Raw inputs do not identify vision/dental or overlap with separately
        # reported LTC/Medicare premiums; do not add those or modeled Medicare.
        medical_premiums = where(
            direct_premiums > 0, direct_premiums, premiums_without_part_b
        )
        return max_(gross - support_paid - spm_unit.sum(medical_premiums), 0)
