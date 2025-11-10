from policyengine_us.model_api import *


class ga_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = ("https://pamms.dhs.ga.gov/dfcs/tanf/1530/",)
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Georgia does not apply deductions to unearned income
        # Use federal TANF gross unearned income variable
        gross_unearned = spm_unit.sum(
            person("tanf_gross_unearned_income", period)
        )
        return gross_unearned
