from policyengine_us.model_api import *


class tn_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.10",
        "Tennessee Administrative Code § 1240-01-50-.10 - Definition of Income",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Earned income includes wages, salaries, self-employment, etc.
        person = spm_unit.members
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        return spm_unit.sum(employment_income + self_employment_income)
