from policyengine_us.model_api import *


class tx_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1320-types-income"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        unearned_income_sources = [
            "social_security",
            "unemployment_compensation",
            "veterans_benefits",
            "alimony_income",
            "child_support_received",
            "gi_cash_assistance",
            "tanf_reported",
        ]

        # Exclude TANF itself from countable income
        person = spm_unit.members
        tanf_reported = spm_unit.sum(person("tanf_reported", period))

        total_unearned = add(spm_unit, period, unearned_income_sources)

        # Subtract TANF to avoid circular dependency
        return total_unearned - tanf_reported
