from policyengine_us.model_api import *


class tx_ottanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Texas One-Time TANF"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2410-general-policy"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Income must be at or below 200% of Federal Poverty Level
        household_income = add(
            spm_unit,
            period,
            ["employment_income", "self_employment_income", "unearned_income"],
        )

        # Get FPL for household size
        household_size = spm_unit("spm_unit_size", period)
        fpg = parameters(period).gov.hhs.fpg
        poverty_guideline = fpg.first_person + fpg.additional_person * max_(
            0, household_size - 1
        )

        # Get OTTANF income limit percentage
        p = parameters(period).gov.states.tx.tanf.ottanf
        income_limit_percentage = p.income_limit_percentage

        income_limit = poverty_guideline * income_limit_percentage

        return household_income <= income_limit
