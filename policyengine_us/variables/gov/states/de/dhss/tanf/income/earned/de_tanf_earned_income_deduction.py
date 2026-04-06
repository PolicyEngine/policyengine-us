from policyengine_us.model_api import *


class de_tanf_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF earned income deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008"
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008: $90 standard work expense from each earner
        p = parameters(period).gov.states.de.dhss.tanf.income

        person = spm_unit.members
        has_earnings = person("tanf_gross_earned_income", period) > 0
        earner_count = spm_unit.sum(has_earnings)

        return earner_count * p.deductions.work_expense
