from policyengine_us.model_api import *


class tn_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.10",
        "Tennessee Administrative Code § 1240-01-50-.10 - Definition of Income",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Unearned income includes Social Security, unemployment, pensions, etc.
        person = spm_unit.members
        income_sources = [
            "social_security",
            "unemployment_compensation",
            "alimony_income",
            "pension_income",
            "disability_benefits",
        ]
        total_unearned = sum(
            person(source, period) for source in income_sources
        )
        return spm_unit.sum(total_unearned)
