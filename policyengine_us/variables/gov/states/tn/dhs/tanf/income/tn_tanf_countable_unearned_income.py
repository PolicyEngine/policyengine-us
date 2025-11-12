from policyengine_us.model_api import *


class tn_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.10",
        "Tennessee Administrative Code § 1240-01-50-.10 - Definition of Income",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Get gross unearned income from federal TANF variable
        # Tennessee does not apply any disregard to unearned income
        person = spm_unit.members
        return spm_unit.sum(person("tanf_gross_unearned_income", period))
